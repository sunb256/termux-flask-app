
```
Ubuntu x86_64
│
├── dist/
│   ├── frontend/
│   ├── python/
│   └── requirements-termux.txt
│
├─ frontend/
│   React + Vite + Tailwind + shadcn
│        │
│        └─ npm run build
│              ↓
│          frontend/dist/
│
├─ backend/
│   Flask + uv
│        │
│        ├─ src/myapp/
│        │     ├─ app.py
│        │     ├─ cli.py
│        │     └─ web/  ← frontend/dist をコピー
│        │
│        └─ uv build --wheel
│              ↓
│          myapp.whl
│
└─ Termux build system
       │
       ├─ cross-pip install Flask等
       ├─ cross-pip install myapp.whl
       │
       ↓
   myapp_xxx_aarch64.deb
       │
       ▼
 Android / Termux
       │
       └─ myapp
             ↓
          Flask
          ├─ /api/*
          └─ React静的ファイル
             ↓
       Chrome
       http://127.0.0.1:5000
```


# Ubuntuに準備
git clone --depth 1 https://github.com/termux/termux-packages.git
cd termux-packages

# ARM64用 Python + uv をビルド


## frontend

## reactの構築

npm create vite@latest src/frontend -- --template react-ts
cd src/frontend
npm install
npm run dev

npm install tailwindcss @tailwindcss/vite
npm install -D @types/node

## tailwindの導入

src/frontend/vite.config.ts
```ts
import path from "path"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  build: {
    outDir: "../../dist/frontend",
    emptyOutDir: true,
  },
})
```

src/frontend/src/index.css
```css
@import "tailwindcss";
```

src/frontend/tsconfig.json
```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ],
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

src/frontend/tsconfig.app.json
```json
{
  "compilerOptions": {
    :
    :
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
```

# shadcn/ui の追加
npx shadcn@latest init
npx shadcn@latest add button

src/frontend/src/App.tsx
```ts
import { Button } from "@/components/ui/button"

function App() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Button>Hello Termux App</Button>
    </div>
  )
}

export default App
```

## prod build
npm run build
-> dist/frontend に出力される



# backend の構築

pyproject.toml
```toml
[project]
name = "app"
version = "0.1.3"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "flask>=3.1,<4",
    "waitress>=3,<4",
]

[build-system]
requires = ["setuptools>=80", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src/backend"]

[tool.setuptools.package-data]
app = [
    "web/*",
    "web/assets/*",
]
```

uv lock
uv sync


mkdir -p src/backend/app


src/backend/app/__init__.py
```py
from .app import create_app

__all__ = ["create_app"]
```

src/backend/app/app.py
src/backend/app/cli.py
を作成 (略)

uv run app

curl http://127.0.0.1:5010/api/health
> {"message":"Flask API is running","status":"ok"}

curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}' \
  http://127.0.0.1:5010/api/echo

> {"message":"hello"}


## react 側 proxy

src/frontend/vite.config.ts
```
  :
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },

```

src/frontend/src/App.tsx を編集

uv run app
cd src/frontend && npm run dev


React
 ↓
Vite
 ↓
Flask API までができた

rpm run build しておく



## react ビルドをflaskにコピー

rm -rf src/backend/app/web
mkdir -p src/backend/app/web

rsync -a \
  dist/frontend/ \
  src/backend/app/web/


uv run app
http://127.0.0.1:5010 へ移動
-> flaskだけで動いている

curl http://127.0.0.1:5010/api/health
> {"message":"Flask API is running","status":"ok"}


## Python wheel を作る
mkdir -p dist/python
uv build --wheel --out-dir dist/python

dist/
├── frontend/
│
└── python/
    └── app-0.1.0-py3-none-any.whl

wheel に React が入ったか確認
sudo apt install unzip
unzip -l dist/python/*.whl

以下があればOKです。

app/__init__.py
app/app.py
app/cli.py

app/web/index.html
app/web/assets/index-xxxx.js
app/web/assets/index-xxxx.css


# 自アプリを作成
uv export \
  --frozen \
  --no-dev \
  --no-emit-project \
  --no-hashes \
  -o dist/requirements-termux.txt


# termux用ビルド、格納
rm -rf termux-packages/sources/app
mkdir -p termux-packages/sources/app/wheels

cp dist/requirements-termux.txt termux-packages/sources/app/
cp dist/python/*.whl termux-packages/sources/app/wheels/

termux-packages/
└── sources/
    └── app/
        ├── requirements-termux.txt
        └── wheels/
            └── app-0.1.0-py3-none-any.whl

mkdir -p termux-packages/packages/app
nano termux-packages/packages/app/build.sh
```

```

rsync -a --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='termux-packages' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='.mypy_cache' \
  --exclude='.ruff_cache' \
  --exclude='dist' \
  --exclude='build' \
  ./ termux-packages/sources/myapp/

mkdir -p termux-packages/sources/myapp/wheels
cp dist/*.whl termux-packages/sources/myapp/wheels/


nano termux-packages/packages/myapp/build.sh

build.sh
```bash
TERMUX_PKG_HOMEPAGE=https://example.com
TERMUX_PKG_DESCRIPTION="React + Flask application"
TERMUX_PKG_LICENSE="non-free"
TERMUX_PKG_MAINTAINER="me"
TERMUX_PKG_VERSION=0.1.0

TERMUX_PKG_SRCURL=file:///home/builder/termux-packages/sources/app
TERMUX_PKG_SHA256=SKIP_CHECKSUM

TERMUX_PKG_DEPENDS="python"
TERMUX_PKG_BUILD_IN_SRC=true

# TermuxのPythonクロスビルド環境をセットアップ
TERMUX_PKG_PYTHON_COMMON_BUILD_DEPS="setuptools, wheel"


termux_step_make() {
    :
}


termux_step_make_install() {
    # Flask / Waitress などの依存パッケージ
    cross-pip install \
        --no-deps \
        --prefix="$TERMUX_PREFIX" \
        -r "$TERMUX_PKG_SRCDIR/requirements-termux.txt"

    # 自作アプリ
    cross-pip install \
        --no-deps \
        --prefix="$TERMUX_PREFIX" \
        "$TERMUX_PKG_SRCDIR"/wheels/*.whl

    # 起動コマンド
    mkdir -p "$TERMUX_PREFIX/bin"

    cat > "$TERMUX_PREFIX/bin/app" <<EOF
#!$TERMUX_PREFIX/bin/bash

exec "$TERMUX_PREFIX/bin/python" \
    -m app.cli \
    "\$@"
EOF

    chmod +x "$TERMUX_PREFIX/bin/app"
}


termux_step_install_license() {
    :
}
```

cd termux-packages


# 実行権限の付与
git ls-files --stage \
  | awk '$1 == "100755" {print $4}' \
  | xargs chmod +x

sudo chmod +x ./build-package.sh


./scripts/run-docker.sh

# docker 内で実行
rm -f ~/.termux-build/_cache-aarch64/*.deb
rm -f ~/.termux-build/_cache-all/*.deb
rm -rf output/offline-bundle

mkdir -p output/offline-bundle
./build-package.sh -f -i app
```
./scripts/run-docker.sh
Running container 'termux-package-builder' from image 'ghcr.io/termux/package-builder'...
WARNING: apparmor_parser not found, AppArmor profiles will not be loaded!
         This is not recommended, as it may cause security issues and unexpected behavior
         Avoid executing untrusted code in the container
 :
 :
 :
INFO: Done ... 0s
INFO: Total OpenMP symbols 2520
INFO: Identifying files with nproc=8
INFO: Done ... 0s
INFO: Found 1 / 1 files
INFO: Running symbol checks on 1 files with nproc=8
INFO: Done ... 0s
termux - build of 'app' done
```

# 依存を追加(コンテナ内)
find ~/.termux-build/_cache-aarch64 \
     ~/.termux-build/_cache-all \
     -maxdepth 1 \
     -type f \
     -name '*.deb' \
     -exec cp -t output/offline-bundle/ {} +
# 自分のアプリも追加
cp output/app_*.deb output/offline-bundle/

# windowsでコピーできるようにファイル名変更
exit
cd output/offline-bundle
for f in *:*; do
    mv -- "$f" "${f//:/_}"
done

vscodeからoutput/offline-bundleダウンロードする

# ホスト側の以下に出力される
termux-packages/output

-> offline-bundleフォルダ一式 を SDカードにコピー

# android側の捜査

Androidのファイル管理アプリで offline-bundleフォルダ一式を をSDカードから内部ストレージの Download にコピー



# termux側

termux-setup-storage
cd ~
mkdir -p ./offline-install
cp ~/storage/downloads/offline-bundle/*.deb ./offline-install

cd ./offline-install
apt install ./*.deb


# アンインストールする場合
apt remove myapp
apt remove app


# 確認
app
chrome でアドレスバーを選択 
http://127.0.0.1:5010 に接続



2回目以降は原則 myapp.deb の更新だけらしい(未確認)

