"""Download pinned, public model weights. No user queries are sent to the hub."""
import json
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAT_MODEL_ID = "Qwen/Qwen3-0.6B"
CHAT_MODEL_REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
EMBEDDING_MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
os.environ.setdefault("HF_HOME", str(ROOT / "models" / ".cache"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install pinned models for offline inference.")
    parser.add_argument("--classifier-only", action="store_true", help="Install only the classifier encoder, without Qwen.")
    parser.add_argument("--force-model-revision", action="store_true", help="Explicitly replace an installed model whose revision differs or cannot be verified.")
    args = parser.parse_args(argv)
    from huggingface_hub import HfApi, snapshot_download
    import yaml

    classifier = yaml.safe_load((ROOT / "config/classifier.yaml").read_text(encoding="utf-8"))
    manifest_path = ROOT / "models/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    models = [("embeddings", classifier["embedding_model"], EMBEDDING_MODEL_REVISION)]
    if not args.classifier_only:
        models.append(("chat", CHAT_MODEL_ID, CHAT_MODEL_REVISION))
    for name, model_id, revision in models:
        model_path = ROOT / "models" / name
        required = [model_path / "config.json", model_path / "tokenizer.json"]
        if name == "embeddings":
            required.extend([model_path / "modules.json", model_path / "1_Pooling/config.json"])
        weights_present = (model_path / "model.safetensors").is_file() or (model_path / "pytorch_model.bin").is_file()
        installed = manifest.get(name)
        same_revision = isinstance(installed, dict) and installed.get("model") == model_id and installed.get("revision") == revision
        if not same_revision and (weights_present or installed is not None) and not args.force_model_revision:
            raise RuntimeError(
                f"Existing {name} weights have a different or unverifiable revision. "
                "Preserving the model volume; use a new volume or --force-model-revision for an intentional replacement."
            )
        if same_revision and weights_present and all(path.is_file() for path in required):
            print(f"{model_id} at {revision} is already installed.", flush=True)
            continue
        info = HfApi().model_info(model_id, revision=revision) if revision else HfApi().model_info(model_id)
        files = [entry.rfilename for entry in info.siblings]
        weights = "*.safetensors" if any(file.endswith(".safetensors") for file in files) else "pytorch_model.bin"
        print(f"Downloading {model_id} at {info.sha}", flush=True)
        snapshot_download(model_id, revision=info.sha, local_dir=ROOT / "models" / name,
                          allow_patterns=[weights, "*.json", "*.txt", "*.model"],
                          ignore_patterns=["onnx/*", "openvino/*"], max_workers=2)
        manifest[name] = {"model": model_id, "revision": info.sha}
        (ROOT / "models/manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("The classifier encoder is installed for offline use." if args.classifier_only
          else "The classifier encoder and free local chat model are installed for offline use.", flush=True)


if __name__ == "__main__":
    main()
