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
