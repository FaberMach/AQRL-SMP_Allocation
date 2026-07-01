# Plano para salvar no GitHub

Destino solicitado:

```text
https://github.com/FaberMach/SMP
```

## Conteudo a versionar

- `README.md`
- `.gitignore`
- `generate_dashboard_data.py`
- `portfolio_rebalance_analysis.py`
- `analysis_outputs/`
- `dashboard/`
- `docs/`

## Conteudo a evitar

- `__pycache__/`
- `_tmp_cookie_copy/`
- `upload_test/`
- `.agents/`

## Comandos esperados quando Git estiver disponivel

```powershell
git init
git remote add origin https://github.com/FaberMach/SMP.git
git checkout -b main
git add README.md .gitignore portfolio_rebalance_analysis.py analysis_outputs dashboard docs
git commit -m "Add SMP portfolio rebalance dashboard"
git push -u origin main
```

Se o repositorio remoto ja tiver historico, usar `git clone` em uma pasta limpa e copiar estes arquivos para la antes do commit.
