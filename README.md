# Gisella Website Docs

## Como rodar em ambiente de desenvolvimento

1. Clonar o repositório
2. Baixar as bibliotecas do python necessárias com:

```bash
uv sync
```

3. Baixar as bibliotecas necessárias para ts e css:

npm:

```bash
npm install
```

pnpm:

```bash
pnpm install
```

4. Ter um terminal rodando o script `dev:css` para garantir que o css a partir do tailwindcss seja construído corretamente.
5. Iniciar o app:

```bash
uv run fastapi dev app
```
