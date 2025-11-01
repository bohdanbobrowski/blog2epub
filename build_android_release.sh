read -s -p "Password: " password
export P4A_RELEASE_KEYSTORE=~/.keystores/bobrowski_com_pl.keystore
export P4A_RELEASE_KEYSTORE_PASSWD="$password"
export P4A_RELEASE_KEYALIAS_PASSWD="$password"
export P4A_RELEASE_KEYALIAS=bobrowski_com_pl
buildozer android release
