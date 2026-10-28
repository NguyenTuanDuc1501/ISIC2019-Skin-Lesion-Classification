def t02_geometry(rgb, method, code):
    assert rgb.shape == (IMG_SIZE, IMG_SIZE, 3)
    if method == 'T02A_HV_R50':
        assert code in range(4)
        if code & 1: rgb = np.flip(rgb, axis=1)
        if code & 2: rgb = np.flip(rgb, axis=0)
    elif method == 'T02B_D4_R50':
        assert code in range(8)
        rgb = np.rot90(rgb, k=code % 4, axes=(0, 1))
        if code >= 4: rgb = np.flip(rgb, axis=1)
    else:
        raise ValueError(method)
    return np.ascontiguousarray(rgb)


    def __init__(self, data, method, train=False):
        assert method in METHODS_T02
        self.data = data.reset_index(drop=True)
        self.method, self.train = method, train


    def __len__(self):
        return len(self.data)


    def __getitem__(self, index):
        row = self.data.iloc[index]
        with Image.open(row.path) as im:
            image = im.convert('RGB').resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)
        if self.train:
            if self.method == 'T02A_HV_R50':
                code = int(torch.rand(()).item() < 0.5) + 2*int(torch.rand(()).item() < 0.5)
            else:
                code = int(torch.randint(8, ()).item())
            image = Image.fromarray(t02_geometry(np.asarray(image), self.method, code))
        return normalize(image), int(row.label)


def t02_loader(data, method, train=False):
    generator = torch.Generator().manual_seed(SEED)
    return DataLoader(T02Dataset(data, method, train), batch_size=BATCH_SIZE,
        shuffle=train, num_workers=NUM_WORKERS, pin_memory=True,
        worker_init_fn=seed_worker, generator=generator, drop_last=False)


def t02_preflight():
    # Kiểm chức năng B00 vẫn nguyên, trước khi chuyển loader tạm thời.
    src = '\n'.join(inspect.getsource(f) for f in [reset_seed, SkinDataset.__init__,
        SkinDataset.__getitem__, SkinDataset.__len__, seed_worker, make_loader,
        build_model, metrics, evaluate, export_evaluation, train_experiment])
    assert hashlib.sha256(src.encode()).hexdigest() == reference['training_source_sha']
    assert sha_file(B00_ROOT/'B00_R50/best_resnet50.pt') == reference['checkpoint_sha']
    assert DEVICE.type == 'cuda', 'Bật GPU T4.'
    assert torch.cuda.get_device_name(0) == b00_config['environment']['gpu']
    for key, value in dict(labels=LABELS, seed=SEED, size=IMG_SIZE, batch=BATCH_SIZE,
        epochs=EPOCHS, patience=PATIENCE, workers=NUM_WORKERS, lr=LR,
        weight_decay=WEIGHT_DECAY).items():
        assert value == b00_config[key], key
    # Kiểm split hiện trong RAM, không chỉ dựa vào số lượng ảnh.
    locked = pd.read_csv(B00_ROOT/'split_manifest.csv', keep_default_na=False)
    cols = ['image','label','label_name','group','file_sha256','split']
    for split in ['train','val','test']:
        pd.testing.assert_frame_equal(
            parts[split][cols].sort_values('image').reset_index(drop=True).astype(str),
            locked.loc[locked.split.eq(split), cols].sort_values('image').reset_index(drop=True).astype(str))
    # Xác nhận tensor validation mới giống pipeline B00, không augmentation.
    sample = parts['val'].groupby('label', group_keys=False).head(2)
    original = SkinDataset(sample, 'B00_R50')
    for method in METHODS_T02:
        candidate = T02Dataset(sample, method, train=False)
        for i in range(len(sample)):
            x, y = original[i]; z, t = candidate[i]
            assert y == t and torch.equal(x, z), 'Validation khác B00.'
    reset_seed(); probe = build_model(); h = hashlib.sha256()
    for key, value in probe.state_dict().items():
        h.update(key.encode()); h.update(value.detach().cpu().numpy().tobytes())
    assert h.hexdigest() == b00_result['initial_sha'], 'Khởi tạo khác B00.'
    del probe; gc.collect(); torch.cuda.empty_cache()


def run_t02(method):
    assert method in METHODS_T02
    t02_preflight()
    branch = T02_ROOT/method
    branch.mkdir(exist_ok=True)
    source = '\n\n'.join(inspect.getsource(f) for f in
        [t02_geometry, T02Dataset.__init__, T02Dataset.__len__,
         T02Dataset.__getitem__, t02_loader, t02_preflight, run_t02])
    spec = {'T02A_HV_R50': 'independent HFlip(p=0.5), VFlip(p=0.5)',
            'T02B_D4_R50': 'uniform code 0..7: rot90(k=code%4), then HFlip if code>=4'}
    config = dict(method=method, reference=reference, baseline_config=b00_config,
        candidate_augmentation=spec[method], augmentation_stage='train only, after RGB resize, before normalization',
        loss='CrossEntropyLoss(weight=None,label_smoothing=0)',
        validation='resize+normalize B00, single view, NO TTA',
        train_from='ImageNet V1; same initial state as B00; NOT B00 checkpoint',
        source_sha=hashlib.sha256(source.encode()).hexdigest(), environment=env)
    next_lock(branch/'candidate_protocol_lock.json', config)
    (branch/'candidate_source.py').write_text(source, encoding='utf-8')
    # Các hàm train/eval gốc tra make_loader và criterion qua globals.
    keys = ['OUT','LOCK_SHA','resume','make_loader','criterion']
    old = {key: globals()[key] for key in keys}
    try:
        globals().update(OUT=branch, LOCK_SHA=sha_file(branch/'candidate_protocol_lock.json'),
            resume=None, make_loader=t02_loader, criterion=nn.CrossEntropyLoss())
        result = train_experiment(method)
    finally:
        globals().update(old)
        gc.collect(); torch.cuda.empty_cache()
    assert result['initial_sha'] == b00_result['initial_sha']
    folder = branch/method
    scores = next_report(pd.read_csv(folder/'val_predictions.csv'), branch/'comparison')
    for key, value in scores.items():
        assert np.isclose(value, result[key], rtol=0, atol=1e-10)
    dump_json(branch/'budget_note.json', dict(
        best_epoch=result['best_epoch'], completed_epochs=result['completed_epochs'],
        best_in_last_two_budget_epochs=result['best_epoch'] >= EPOCHS-1,
        interpretation='Late best suggests checking budget limits; does not justify increasing epochs for this branch alone.'))
    print(method, result)
    return result
