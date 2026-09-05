
# Ubuntuに準備
git clone --depth 1 https://github.com/termux/termux-packages.git
cd termux-packages

# ARM64用 Python + uv をビルド
sudo chmod +x ./scripts/run-docker.sh
./scripts/run-docker.sh ./build-package.sh -a aarch64 python python-pip uv

# ビルド後
termux-packages/output/

# 自アプリを作成

# 作成後ビルドして格納
mkdir -p termux-packages/sources/myapp

rsync -a --delete \
  --exclude='.git' \
  --exclude='termux-packages' \
  ./ termux-packages/sources/myapp/

nano termux-packages/packages/myapp/build.sh

build.sh
```bash
TERMUX_PKG_HOMEPAGE=https://example.com
TERMUX_PKG_DESCRIPTION="My Python application"
TERMUX_PKG_LICENSE="MIT"
TERMUX_PKG_MAINTAINER="me"
TERMUX_PKG_VERSION=0.1.0

TERMUX_PKG_SRCURL=file:///home/builder/termux-packages/sources/myapp
TERMUX_PKG_SHA256=SKIP_CHECKSUM

TERMUX_PKG_DEPENDS="python"
TERMUX_PKG_PLATFORM_INDEPENDENT=true
TERMUX_PKG_BUILD_IN_SRC=true

termux_step_make() {
    :
}

termux_step_make_install() {
    mkdir -p "$TERMUX_PREFIX/lib/myapp"
    cp -a . "$TERMUX_PREFIX/lib/myapp/"
}
```