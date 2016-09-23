#! /bin/bash
ln -fs `pwd`/autoexam.py /usr/bin/autoexam &&
chmod +x /usr/bin/autoexam &&
ln -fs `pwd`/completion.sh /usr/share/bash-completion/completions/autoexam &&
echo "Done... run 'autoexam -h' for help."
