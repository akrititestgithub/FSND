source setup.sh
dropdb capstone_test
createdb capstone_test
psql capstone_test < capstone_test_file.psql
python test_app.py