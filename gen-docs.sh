pdoc --html --html-dir docs pique.pq --overwrite
pdoc --html --html-dir docs pique.cli --overwrite
pdoc --html --html-dir docs pique.themes --overwrite
mv docs/pique/* docs
rm -rf docs/pique
