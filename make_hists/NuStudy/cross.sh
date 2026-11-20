# cross section
export VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi
export RUNJSON=Nu_p${VERSION}_run
python ../nu_extract/ExtractorClasses.py NuCrossAllP${VERSION}.json >& cross_P${VERSION}.log