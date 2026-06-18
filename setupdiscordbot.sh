function setup(){
    python3 -m venv discordvenv
    source discordvenv/bin/activate
    pip install -r requirements.txt && playwright install chromium
    export discordtoken=$1
}

function run(){
    source discordvenv/bin/activate
    python3 -m discord.bot
}

function show_help {
    echo "Usage: $0 [options]"
    echo "Options:" 
    echo "  --setup"
    echo "  --run"
}

function parse_options {
    while :; do
        case $1 in
            -h|-\?|--help)
            show_help
            exit
            ;;
            --setup)
            setup
            exit
            ;;
            --run)
            run
            exit
            ;;
            -?*)
            printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2 
            ;;
            *)
            break
        esac
        shift
    done
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_options "$@"
    run
fi