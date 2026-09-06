Termux:Widget のバックグラウンドタスク + termux-open-url を使えば、ホーム画面のアイコンを1回タップするだけで、

Flaskを起動
少し待つ
Androidブラウザで http://127.0.0.1:5000 を開く

まで自動化できます。

Termux:Widget は ~/.shortcuts/tasks/ 配下のスクリプトをバックグラウンド実行できます。 また termux-open-url はTermux標準の termux-tools に含まれ、Androidのブラウザ等へURLを渡せます。

Termuxでこれを作ってください。

```bash
mkdir -p ~/.shortcuts/tasks

cat > ~/.shortcuts/tasks/myapp <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# Flaskが既に起動していなければ起動
if ! pgrep -f 'python.*flask.*--app app' >/dev/null; then
    myapp > "$HOME/myapp.log" 2>&1 &
fi

# Flask起動を少し待つ
sleep 2

# Androidブラウザで開く
termux-open-url http://127.0.0.1:5000
EOF
```

chmod 700 ~/.shortcuts/tasks/myapp