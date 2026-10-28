from torch.utils.data import Dataset, DataLoader

def reset_seed():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def seed_worker(worker_id):
    seed = torch.initial_seed() % (2**32)
    random.seed(seed); np.random.seed(seed)

def build_model():
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, len(LABELS))
    return model.to(DEVICE)

def metrics(y, pred):
    return dict(accuracy=float(accuracy_score(y, pred)),
        macro_f1=float(f1_score(y, pred, labels=range(8), average='macro', zero_division=0)),
        balanced_accuracy=float(balanced_accuracy_score(y, pred)))

def evaluate(model, loader):
    model.eval()
    loss_sum, total, labels, probabilities = 0.0, 0, [], []
    with torch.no_grad():
        for images, y in loader:
            images, y = images.to(DEVICE), y.to(DEVICE)
            logits = model(images)
            loss_sum += criterion(logits, y).item() * len(y)
            total += len(y)
            labels.extend(y.cpu().tolist())
            probabilities.append(logits.softmax(1).cpu().numpy())
    probabilities = np.concatenate(probabilities)
    pred = probabilities.argmax(1)
    return loss_sum / total, metrics(labels, pred), np.array(labels), pred, probabilities

def export_evaluation(model, data, method, folder, split):
    loss, scores, y, pred, probs = evaluate(model, make_loader(data, method))
    result = data[['image', 'group', 'file_sha256', 'label_name']].rename(columns={'label_name':'true_label'}).copy()
    result['pred_label'] = [LABELS[i] for i in pred]
    for i, label in enumerate(LABELS): result['p_' + label] = probs[:, i]
    result.to_csv(folder / f'{split}_predictions.csv', index=False)
    report = classification_report(y, pred, labels=range(8), target_names=LABELS, output_dict=True, zero_division=0)
    pd.DataFrame(report).T.to_csv(folder / f'{split}_per_class.csv')
    cm = confusion_matrix(y, pred, labels=range(8))
    pd.DataFrame(cm, index=LABELS, columns=LABELS).to_csv(folder / f'{split}_confusion.csv')
    fig, ax = plt.subplots(figsize=(7, 6)); ax.imshow(cm, cmap='Blues')
    ax.set(xticks=range(8), yticks=range(8), xticklabels=LABELS, yticklabels=LABELS,
           xlabel='Dự đoán', ylabel='Nhãn thật', title=f'{method} — {split}')
    for i in range(8):
        for j in range(8): ax.text(j, i, str(cm[i,j]), ha='center', va='center', color='white' if cm[i,j] > cm.max()/2 else 'black', fontsize=8)
    fig.tight_layout(); fig.savefig(folder / f'{split}_confusion.png', dpi=140); plt.close(fig)
    dump_json(folder / f'{split}_metrics.json', dict(loss=loss, **scores))
    return scores

def train_experiment(method):
    assert DEVICE.type == 'cuda', 'Bật GPU; không train ResNet50 trên CPU.'
    folder = OUT / method
    if not folder.exists() and resume and (resume / method / 'complete.json').exists():
        shutil.copytree(resume / method, folder)
    folder.mkdir(exist_ok=True)
    complete_path = folder / 'complete.json'
    if complete_path.exists():
        saved = json.loads(complete_path.read_text())
        assert saved['lock_sha'] == LOCK_SHA
        assert sha_file(folder / 'best_resnet50.pt') == saved['checkpoint_sha']
        print(method, 'đã hoàn thành; tái sử dụng kết quả, không train lại.')
        return saved
    if (folder / 'history.csv').exists():
        raise RuntimeError('Lượt train trước chưa hoàn thành. Giữ output đó; dùng OUT mới để chạy lại cả protocol, không âm thầm resume optimizer.')
    reset_seed()
    model = build_model()
    # Hash khởi tạo: xác minh hai lượt khởi tạo giống nhau.
    initial = hashlib.sha256()
    for key, value in model.state_dict().items():
        initial.update(key.encode()); initial.update(value.detach().cpu().numpy().tobytes())
    init_sha = initial.hexdigest()
    train_loader = make_loader(parts['train'], method, train=True)
    val_loader = make_loader(parts['val'], method)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    best, wait, history = -1.0, 0, []
    started = time.perf_counter()
    for epoch in range(1, EPOCHS + 1):
        model.train(); loss_sum = 0.0; total = 0
        for images, y in train_loader:
            images, y = images.to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, y)
            loss.backward(); optimizer.step()
            loss_sum += loss.item() * len(y); total += len(y)
        val_loss, scores, _, _, _ = evaluate(model, val_loader)
        history.append(dict(epoch=epoch, train_loss=loss_sum/total, val_loss=val_loss,
                            lr=optimizer.param_groups[0]['lr'], **scores))
        pd.DataFrame(history).to_csv(folder / 'history.csv', index=False)
        print(f'{method} epoch {epoch:02d}: train={loss_sum/total:.4f}, val={val_loss:.4f}, F1={scores["macro_f1"]:.4f}')
        if scores['macro_f1'] > best + 1e-5:
            best, best_epoch, wait = scores['macro_f1'], epoch, 0
            torch.save(model.state_dict(), folder / 'best_resnet50.pt')
        else:
            wait += 1
        scheduler.step()
        if wait >= PATIENCE: break
    model.load_state_dict(torch.load(folder / 'best_resnet50.pt', map_location=DEVICE, weights_only=True))
    scores = export_evaluation(model, parts['val'], method, folder, 'val')
    h = pd.DataFrame(history)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(h.epoch, h.train_loss, label='train'); axes[0].plot(h.epoch, h.val_loss, label='val'); axes[0].legend()
    axes[1].plot(h.epoch, h.macro_f1); axes[1].set_title('Validation macro-F1')
    for ax in axes: ax.set_xlabel('Epoch'); ax.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(folder / 'learning_curves.png', dpi=120); plt.close(fig)
    saved = dict(method=method, lock_sha=LOCK_SHA, initial_sha=init_sha,
        checkpoint_sha=sha_file(folder / 'best_resnet50.pt'), best_epoch=best_epoch,
        completed_epochs=len(history), seconds=time.perf_counter()-started, **scores)
    dump_json(complete_path, saved)
    del model, optimizer, train_loader, val_loader
    torch.cuda.empty_cache()
    return saved

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

class T02Dataset(Dataset):
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

def t02_bootstrap(predictions, n_boot=2000, seed=20261007):
    names = list(predictions)
    base = predictions[names[0]].sort_values('image').reset_index(drop=True)
    required = ['image','group','file_sha256','true_label']
    assert base.image.is_unique and base.groupby('group').true_label.nunique().max() == 1
    aligned = []
    for name in names:
        df = predictions[name].sort_values('image').reset_index(drop=True)
        assert df.image.is_unique
        pd.testing.assert_frame_equal(base[required].astype(str), df[required].astype(str))
        ids = df.pred_label.map(label_to_id)
        assert ids.notna().all()
        aligned.append(ids.to_numpy(dtype=int))
    y = base.true_label.map(label_to_id).to_numpy(dtype=int)
    codes, groups = pd.factorize(base.group, sort=True)
    group_y = np.array([y[np.flatnonzero(codes == g)[0]] for g in range(len(groups))])
    strata = [np.flatnonzero(group_y == k) for k in range(8)]
    assert all(len(s) > 0 for s in strata)
    # Mỗi group giữ mọi ảnh của nó. Chỉ lấy lại group, không lấy lại từng ảnh độc lập.
    counts = np.zeros((len(names), len(groups), 8), dtype=np.int64)
    for model_id, pred in enumerate(aligned):
        np.add.at(counts[model_id], (codes, pred), 1)
    def macro(cm):
        tp = np.diagonal(cm, axis1=-2, axis2=-1)
        denom = cm.sum(axis=-1) + cm.sum(axis=-2)
        return np.divide(2*tp, denom, out=np.zeros_like(tp, dtype=float), where=denom>0).mean(axis=-1)
    observed_cm = np.stack([confusion_matrix(y, pred, labels=range(8)) for pred in aligned])
    observed = macro(observed_cm)
    rng = np.random.default_rng(seed)
    draws = np.empty((n_boot, len(names)))
    for b in range(n_boot):
        cm = np.zeros((len(names), 8, 8), dtype=np.int64)
        for label, ids in enumerate(strata):
            chosen = rng.choice(ids, size=len(ids), replace=True)
            cm[:, label, :] = counts[:, chosen, :].sum(axis=1)
        draws[b] = macro(cm)
    pairs = [(i,0) for i in range(1,len(names))]
    if len(names) == 3: pairs.append((2,1))  # B so với A, bổ sung mô tả.
    records = []
    for i,j in pairs:
        delta = 100*(draws[:,i]-draws[:,j])
        lo,hi = np.quantile(delta, [0.025,0.975])
        records.append(dict(candidate=names[i], reference=names[j],
            delta_macro_f1_pp=100*(observed[i]-observed[j]),
            ci95_low_pp=float(lo), ci95_high_pp=float(hi), n_boot=n_boot,
            contains_zero=bool(lo<=0<=hi)))
    group_support = pd.DataFrame(dict(label=LABELS, n_groups=[len(s) for s in strata]))
    return pd.DataFrame(records), pd.DataFrame(draws,columns=names), group_support
