sudo apt-get install -y lxml python-lxml libxml2-dev libxslt-dev
sudo apt-get install -y python-numpy
pip install mechanize
pip install BeautifulSoup4
pip install mechanize
pip install lxml
pip install cssselect


#pip install nltk
#sudo apt-get install python-tk

pip install sqlalchemy
easy_install -U distribute
pip install sqlautocode

sudo apt-get install python-mysqldb
sudo apt-get install libmysqlclient-dev

sudo apt-get install sqlitebrowser

# install local mysql database
sudo apt-get install mysql-client-5.5
sudo apt-get install mysql-server-5.5

# creating database of py-gameday
mysqladmin create gameday -u root -p
mysql -D gameday < gameday.sql -u root -p


############# new way ########################

apt-get install libxml2-dev libxslt-dev

