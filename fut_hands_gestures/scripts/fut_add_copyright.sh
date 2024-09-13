#!/bin/bash
# Setting parameters for copyright
authors="Murilo Cruz Lopes, Ludwing Ferney Marenco Camacho"
company="INATEL"



# add copyright
find ./* -regex ".*\.\(py\|yaml\)" -print0 |
while IFS= read -r -d '' file; do
    if grep -q "Creation Date:" "$file"; then
        :
    else
        sed -i "1 i# Creation Date: $(date "+%Y-%m-%d")\n# Authors $authors\n# Developed by: Inatel Competence Center\n# Copyright $(date "+%Y"), $company.\n# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner\n" $file
    fi
    checkauthor=`grep -icx "${authors}" $file`
    checkcompany=`grep -icx "${company}" $file`
    if [[ $author -ne 0  &&  $checkcompany -ne 0 ]]
    then
        :
    else
        sed -i '/# Creation/d' $file
        sed -i '/# Authors/d' $file
        sed -i '/# Copyright/d' $file
        sed -i '/# All rights/d' $file
        sed -i '/# Developed/d' $file
        sed -i "1 i# Creation Date: $(date "+%Y-%m-%d")\n# Authors $authors\n# Developed by: Inatel Competence Center\n# Copyright $(date "+%Y"), $company.\n# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner" $file
    fi
done
grep -q "Creation Date:" Jenkinsfile || sed -i "1 i// Creation Date: $(date "+%Y-%m-%d")\n// Authors $authors\n// Developed by: Inatel Competence Center\n// Copyright $(date "+%Y"), $company.\n// All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner.\n" Jenkinsfile
grep -q "Creation Date:" Dockerfile || sed -i "1 i# Creation Date: $(date "+%Y-%m-%d")\n# Authors $authors\n# Developed by: Inatel Competence Center\n# Copyright $(date "+%Y"), $company.\n# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner.\n" Dockerfile

checkauthor=`grep -icx "${authors}" Jenkinsfile`
checkcompany=`grep -icx "${company}" Jenkinsfile`

if [[ $checkauthor -ne 1 && $checkcompany -ne 1 ]]; then
    sed -i '/Creation/d' Jenkinsfile
    sed -i '/Authors/d' Jenkinsfile
    sed -i '/Copyright/d' Jenkinsfile
    sed -i '/All rights/d' Jenkinsfile
    sed -i '/Developed/d' Jenkinsfile
    sed -i "1 i// Creation Date: $(date "+%Y-%m-%d")\n// Authors $authors\n// Developed by: Inatel Competence Center\n// Copyright $(date "+%Y"), $company.\n// All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner." Jenkinsfile
fi

checkauthor=`grep -icx "${authors}" Dockerfile`
checkcompany=`grep -icx "${company}" Dockerfile`

if [[ $checkauthor -ne 1 && $checkcompany -ne 1 ]]; then
    sed -i '/# Creation/d' Dockerfile
    sed -i '/# Authors/d' Dockerfile
    sed -i '/# Copyright/d' Dockerfile
    sed -i '/# All rights/d' Dockerfile
    sed -i '/# Developed/d' Dockerfile
    sed -i "1 i# Creation Date: $(date "+%Y-%m-%d")\n# Authors $authors\n# Developed by: Inatel Competence Center\n# Copyright $(date "+%Y"), $company.\n# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner." Dockerfile
else
    :
fi