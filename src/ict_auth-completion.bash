_ict_auth_completion() {
    local cur prev opts commands options
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="login logout status enable disable logs upgrade uninstall"

    options="-h --help -V --version"

    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${options}" -- ${cur}) )
    else
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
    fi
}

complete -F _ict_auth_completion ict_auth