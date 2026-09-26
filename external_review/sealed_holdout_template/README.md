# Sealed Mini-Holdout Template

The contributor prepares a `runtime/` directory containing one or more case directories with `case.yaml` and `spec.yaml`, plus a separately sealed `labels/` directory. Source metadata belongs in `sources/SOURCE_REGISTER.json`.

The evaluator receives only `runtime/`. Run:

```text
python scripts/run_sealed_holdout.py <runtime-directory> <results.json>
```

The runner never imports or reads labels. After the result file and its hash are frozen, an independent scorer may compare it with the separately delivered hidden labels. Do not put expected status, pathology, or match fields into runtime files.

Copy the example files, replace all placeholders, and rename `case.example.yaml` to `case.yaml` and `spec.example.yaml` to `spec.yaml` inside `runtime/cases/<case-id>/`.

