if type -p java; then
    echo found java executable in PATH
    _java=java
elif [[ -n "$JAVA_HOME" ]] && [[ -x "$JAVA_HOME/bin/java" ]];  then
    echo found java executable in JAVA_HOME
    _java="$JAVA_HOME/bin/java"
else
    echo "no java"
fi

if [[ "$_java" ]]; then
    version=$("$_java" -version 2>&1 | awk -F '"' '/version/ {print $2}')
    echo Java version "$version"
    # if [[ "$version" == "17" ]]; then
    if [[ ${version:0:2} == "17" ]]; then
        read -s -p "Password: " password
        export P4A_RELEASE_KEYSTORE=~/.keystores/bobrowski_com_pl_pkcs12.keystore
        export P4A_RELEASE_KEYSTORE_PASSWD="$password"
        export P4A_RELEASE_KEYALIAS_PASSWD="$password"
        export P4A_RELEASE_KEYALIAS=bobrowski_com_pl
        buildozer android release
    else
        echo This script requires Java version == 17
    fi
fi


