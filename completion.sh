# bash completion for autoexam

_autoexam()
{
    local cur prev words cword
    _init_completion || return

    local special i
    for (( i=0; i < ${#words[@]}-1; i++ )); do
        if [[ ${words[i]} == @(list|search|show|update|install|remove|upgrade|full-upgrade|edit-sources|dist-upgrade|purge) ]]; then
            special=${words[i]}
        fi
    done


    COMPREPLY=( $( compgen -W '-h --help new review gen scan status edit stats
        webpoll ui report grade qtui' -- "$cur" ) )

    return 0
} &&
complete -F _autoexam autoexam

# ex: ts=4 sw=4 et filetype=sh
