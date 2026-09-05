
```
Ubuntu x86_64
  │
  │  Pythonアプリを開発
  │  uv / pyproject.toml / uv.lock
  │
  ▼
Termux公式 build system
  │
  │ Android ARM64向けに依存を準備
  │ Android NDK / cross-pip
  │
  ▼
myapp_xxx_aarch64.deb
+
python / python-pip / openssl ... の .deb
  │
  ▼
offline-bundle
  │
  ▼
Windows → SDカード
  │
  ▼
Android 14 / Termux
  │
  │ apt install ./*.deb
  ▼
myapp
  │
  ▼
Flask
  │
  ▼
Androidブラウザ
http://127.0.0.1:5000
```


# Ubuntuに準備
git clone --depth 1 https://github.com/termux/termux-packages.git
cd termux-packages

# ARM64用 Python + uv をビルド


# ビルド後
termux-packages/output/

# 自アプリを作成
uv build --wheel
uv export \
  --frozen \
  --no-dev \
  --no-emit-project \
  --no-hashes \
  -o requirements-termux.txt


# 作成後ビルドして格納
mkdir -p termux-packages/sources/myapp

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
TERMUX_PKG_DESCRIPTION="My Python application"
TERMUX_PKG_LICENSE="non-free"
TERMUX_PKG_MAINTAINER="me"
TERMUX_PKG_VERSION=0.1.1

TERMUX_PKG_SRCURL=file:///home/builder/termux-packages/sources/myapp
TERMUX_PKG_SHA256=SKIP_CHECKSUM

TERMUX_PKG_DEPENDS="python"
TERMUX_PKG_BUILD_IN_SRC=true

# これを指定するとTermuxのPythonクロスビルド環境がセットアップされる
TERMUX_PKG_PYTHON_COMMON_BUILD_DEPS="setuptools, wheel"

termux_step_make() {
    :
}

termux_step_make_install() {
    # Flaskなど依存パッケージ
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

    cat > "$TERMUX_PREFIX/bin/myapp" <<EOF
#!$TERMUX_PREFIX/bin/bash
exec "$TERMUX_PREFIX/bin/python" \
    -m flask \
    --app app \
    run \
    --host 0.0.0.0 \
    "\$@"
EOF

    chmod +x "$TERMUX_PREFIX/bin/myapp"
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
./build-package.sh -f -i myapp


```
 ./scripts/run-docker.sh
Running container 'termux-package-builder' from image 'ghcr.io/termux/package-builder'...
WARNING: apparmor_parser not found, AppArmor profiles will not be loaded!
         This is not recommended, as it may cause security issues and unexpected behavior
         Avoid executing untrusted code in the container
builder@503ae370a5bf:~/termux-packages$ ./build-package.sh -f -I myapp
termux - building myapp for arch aarch64...
[packages-cf.termux.dev-apt-termux-main]: Downloading https://packages-cf.termux.dev/apt/termux-main/dists/stable/Release
[packages-cf.termux.dev-apt-termux-main]:   % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
[packages-cf.termux.dev-apt-termux-main]:                                  Dload  Upload  Total   Spent   Left   Speed
[packages-cf.termux.dev-apt-termux-main]: 
[packages-cf.termux.dev-apt-termux-main]:   0      0   0      0   0      0      0      0                              0
[packages-cf.termux.dev-apt-termux-main]: 100  13133 100  13133   0      0 168.6k      0                              0
 :
 :
 :
[notice] A new release of pip is available: 26.1.2 -> 26.2.1
[notice] To update, run: pip install --upgrade pip
INFO: READELF=llvm-readelf ... /home/builder/.termux-build/_cache/android-r29-api-24-v5/bin/llvm-readelf
INFO: Generating undefined symbols regex to /tmp/tmp.ATSb0VCJX5
INFO: Done ... 0s
INFO: Total symbols 2372
INFO: Generating OpenMP symbols regex to /tmp/tmp.vjg0Ma6vwP
INFO: Done ... 0s
INFO: Total OpenMP symbols 2520
INFO: Identifying files with nproc=8
INFO: Done ... 0s
INFO: Found 1 / 1 files
INFO: Running symbol checks on 1 files with nproc=8
INFO: Done ... 1s
termux - build of 'myapp' done
```

# 依存を追加
find ~/.termux-build/_cache-aarch64 \
     ~/.termux-build/_cache-all \
     -maxdepth 1 \
     -type f \
     -name '*.deb' \
     -exec cp -t output/offline-bundle/ {} +
# 自分のアプリも追加
cp output/myapp_*.deb output/offline-bundle/
# windowsでコピーできるようにファイル名変更
cd output/offline-bundle
for f in *:*; do
    mv -- "$f" "${f//:/_}"
done

vscodeからダウンロードする

# ホスト側の以下に出力される
termux-packages/output

-> SDカードにコピー

Androidのファイル管理アプリで .deb をSDカードから内部ストレージの Download にコピー


termux-setup-storage
cd ~
mkdir -p ./offline-install
cp ~/storage/downloads/offline-bundle/*.deb ./offline-install

cd ./offline-install
apt install ./*.deb


# アンインストールする場合
apt remove myapp


# 確認
chrome で http://127.0.0.1:5000 に接続


2回目以降は原則 myapp.deb の更新だけ

