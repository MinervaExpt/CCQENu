cp $1 $1.backup
jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook $1.backup --stdout   --log-level=ERROR > $1
