# RAGアプリケーションの使い方

このドキュメントでは、RAGアプリケーションの環境構築、DB操作、および実行方法について説明します。

## 注意事項 (重要)

- **`.env` ファイルの設定:** アプリケーション実行前に、必ず `.env` ファイルに `OPENAI_API_KEY` を設定してください。`.env` ファイルに `OPENAI_API_KEY=YOUR_API_KEY` のように記述します。APIキーが設定されていない場合、スクリプトは正常に動作しません。
- **`uv sync` の実行:** `uv sync` コマンドは、プロジェクトの依存関係を更新するために使用します。環境変更後、または新しいライブラリをインストールした後は必ず実行してください。

## Langfuseを使う場合

Langfuseを使用する場合の手順は以下の通りです。

まず、GitとDockerがインストールされ、アクティブになっていることを確認してください（そうでない場合は、Docker Desktopアプリを開いてください）。
コマンドプロンプト/PowerShellで以下を入力します。

```bash
git clone https://github.com/langfuse/langfuse.git
```

次に、同じターミナルで以下を入力します。

```bash
cd langfuse
```

最後に、ターミナルで以下を入力します。

```bash
docker compose up
```

このステップには数分かかる場合があります。

ローカルサーバーが起動し、以下を使用してアクセスできます。

```
http://localhost:3000
```

または

```
http://0.0.0.0:3000
```

## 環境構築

### 環境の同期

以下のコマンドを実行して、プロジェクトに必要な環境を同期してください。

```bash
uv sync
```

このコマンドは、`pyproject.toml` ファイルに記述された依存関係をインストールし、プロジェクトで使用するPython環境を整えます。

## DB操作

### DB作成

DBを作成するには、以下の手順に従ってください。

1.  `db` ディレクトリ内に、必要な条件を満たすDBが存在するか確認してください。DB名、データセット、チャンクサイズなどの条件が一致するものがあるかを確認します。
2.  必要なDBがない場合は、以下のコマンドを実行してDBを作成します。

```bash
uv run src/db_management/create_db.py
```

上記のコマンドを実行すると、`src/db_management/create_db.py` スクリプトが実行され、ChromaDBが作成されます。このスクリプトは、指定されたPDFファイルからテキストを抽出し、OpenAI APIを使用してベクトル埋め込みを生成し、ChromaDBに保存します。

### DBリセット

DBをリセット（初期化）するには、以下のコマンドを実行します。

```bash
uv run src/db_management/reset_db.py
```

このスクリプトは、既存のDBを削除し、新しい空のDBを作成します。DBの内容を完全に消去したい場合に実行してください。

### DB削除

DBを完全に削除するには、以下のコマンドを実行します。

```bash
uv run src/db_management/delete_db.py
```

このスクリプトは、DBファイルと関連するメタデータを完全に削除します。DBが不要になった場合に実行してください。

## RAG実行

RAG (Retrieval-Augmented Generation) を実行するには、`src/rag/sample.py` スクリプトを使用します。

```bash
uv run src/rag/sample.py
```

## RAG評価実行

RAG評価 (Retrieval-Augmented Generation Evaluation) を実行するには、`src/rag-evaluation/sample.py` スクリプトを使用します。

```bash
uv run src/rag-evaluation/sample.py
```

FlagEmbeddingによってインストールされたモデルは、デフォルトで `/Users/<YourUsername>/.cache/huggingface/transformers` ディレクトリに保存されます。

## 設定ファイル

設定ファイル `config.py` には、RAGアプリケーションの動作をカスタマイズするためのパラメータが定義されています。必要に応じて、このファイルの内容を変更してください。
