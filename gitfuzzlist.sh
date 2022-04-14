#!/bin/bash
#create directory fuzzing list from github repo
git clone $1.git
repo=$(basename $1)
cd $repo
{
    git rev-list --objects --all
    git rev-list --objects -g --no-walk --all
    git rev-list --objects --no-walk \
        $(git fsck --unreachable |
          grep '^unreachable commit' |
          cut -d' ' -f3)
} | awk '{print $2}' | sort -u >../$repo-fuzz.txt
cd ..
rm -rf $repo
echo ""
echo "Git generated fuzzlist is located at $repo-fuzz.txt"
