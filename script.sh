#!/usr/bin/env bash
set -e

APP_NAME="nobetci"
CONFIG_DIR="/etc/opt/$APP_NAME"
DATA_DIR="/var/lib/$APP_NAME"
COMPOSE_FILE="$CONFIG_DIR/docker-compose.yml"
ENV_FILE="$CONFIG_DIR/.env"
PANEL_ADDRESS=""
PANEL_USER=""
PANEL_PASSWORD=""
PANEL_TYPE=""
SYNC_WITH_PANEL=False
SECRET_KEY=""
API_USERNAME=""
API_PASSWORD=""

FETCH_REPO="muttehit/nobetci"
SCRIPT_URL="https://github.com/$FETCH_REPO/raw/main/script.sh"

colorized_echo() {
    local color=$1
    local text=$2

    case $color in
        "red")
        printf "\e[91m${text}\e[0m\n";;
        "green")
        printf "\e[92m${text}\e[0m\n";;
        "yellow")
        printf "\e[93m${text}\e[0m\n";;
        "blue")
        printf "\e[94m${text}\e[0m\n";;
        "magenta")
        printf "\e[95m${text}\e[0m\n";;
        "cyan")
        printf "\e[96m${text}\e[0m\n";;
        *)
            echo "${text}"
        ;;
    esac
}

check_running_as_root() {
    if [ "$(id -u)" != "0" ]; then
        colorized_echo red "This command must be run as root."
        exit 1
    fi
}

detect_os() {
    # Detect the operating system
    if [ -f /etc/lsb-release ]; then
        OS=$(lsb_release -si)
        elif [ -f /etc/os-release ]; then
        OS=$(awk -F= '/^NAME/{print $2}' /etc/os-release | tr -d '"')
        elif [ -f /etc/redhat-release ]; then
        OS=$(cat /etc/redhat-release | awk '{print $1}')
        elif [ -f /etc/arch-release ]; then
        OS="Arch"
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

detect_and_update_package_manager() {
    colorized_echo blue "Updating package manager"
    if [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        PKG_MANAGER="apt-get"
        $PKG_MANAGER update
        elif [[ "$OS" == "CentOS"* ]] || [[ "$OS" == "AlmaLinux"* ]]; then
        PKG_MANAGER="yum"
        $PKG_MANAGER update -y
        $PKG_MANAGER install -y epel-release
        elif [ "$OS" == "Fedora"* ]; then
        PKG_MANAGER="dnf"
        $PKG_MANAGER update
        elif [ "$OS" == "Arch" ]; then
        PKG_MANAGER="pacman"
        $PKG_MANAGER -Sy
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

detect_compose() {
    # Check if docker compose command exists
    if docker compose >/dev/null 2>&1; then
        COMPOSE='docker compose'
        elif docker-compose >/dev/null 2>&1; then
        COMPOSE='docker-compose'
    else
        colorized_echo red "docker compose not found"
        exit 1
    fi
}

install_package () {
    if [ -z $PKG_MANAGER ]; then
        detect_and_update_package_manager
    fi

    PACKAGE=$1
    colorized_echo blue "Installing $PACKAGE"
    if [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        $PKG_MANAGER -y install "$PACKAGE"
        elif [[ "$OS" == "CentOS"* ]] || [[ "$OS" == "AlmaLinux"* ]]; then
        $PKG_MANAGER install -y "$PACKAGE"
        elif [ "$OS" == "Fedora"* ]; then
        $PKG_MANAGER install -y "$PACKAGE"
        elif [ "$OS" == "Arch" ]; then
        $PKG_MANAGER -S --noconfirm "$PACKAGE"
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

install_docker() {
    # Install Docker and Docker Compose using the official installation script
    colorized_echo blue "Installing Docker"
    curl -fsSL https://get.docker.com | sh
    colorized_echo green "Docker installed successfully"
}

install_nobetci_script() {
    colorized_echo blue "Installing nöbetci script"
    curl -sSL $SCRIPT_URL | install -m 755 /dev/stdin /usr/local/bin/nobetci
    colorized_echo green "nöbetci script installed successfully"
}

install_nobetci() {
    # Fetch releases
    FILES_URL_PREFIX="https://raw.githubusercontent.com/muttehit/nobetci/master"
	COMPOSE_FILES_URL="https://raw.githubusercontent.com/muttehit/nobetci/master/deploy"
 	database=$1
  	nightly=$2
  
    mkdir -p "$DATA_DIR"
    mkdir -p "$CONFIG_DIR"

    colorized_echo blue "Fetching compose file"
    curl -sL "$COMPOSE_FILES_URL/docker-compose-$database.yml" -o "$CONFIG_DIR/docker-compose.yml"
    colorized_echo green "File saved in $CONFIG_DIR/docker-compose.yml"
	if [ "$nightly" = true ]; then
	    colorized_echo red "setting compose tag to nightly."
	 	sed -ri "s/(ghcr.io\/muttehit\/nobetci:)latest/\1nightly/g" $CONFIG_DIR/docker-compose.yml
	fi
 
    colorized_echo blue "Fetching example .env file"
    curl -sL "$FILES_URL_PREFIX/.env.example" -o "$ENV_FILE"
    colorized_echo green "File saved in $ENV_FILE"

    colorized_echo green "Nöbetci files downloaded successfully"
}

uninstall_nobetci_script() {
    if [ -f "/usr/local/bin/nobetci" ]; then
        colorized_echo yellow "Removing nöbetci script"
        rm "/usr/local/bin/nobetci"
    fi
}

uninstall_nobetci() {
    if [ -d "$CONFIG_DIR" ]; then
        colorized_echo yellow "Removing directory: $CONFIG_DIR"
        rm -r "$CONFIG_DIR"
    fi
}

uninstall_nobetci_docker_images() {
    images=$(docker images | grep nobetci | awk '{print $3}')

    if [ -n "$images" ]; then
        colorized_echo yellow "Removing Docker images of Nöbetci"
        for image in $images; do
            if docker rmi "$image" >/dev/null 2>&1; then
                colorized_echo yellow "Image $image removed"
            fi
        done
    fi
}

uninstall_nobetci_data_files() {
    if [ -d "$DATA_DIR" ]; then
        colorized_echo yellow "Removing directory: $DATA_DIR"
        rm -r "$DATA_DIR"
    fi
}

up_nobetci() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" up -d --remove-orphans
}

down_nobetci() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" down
}

show_nobetci_logs() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" logs
}

follow_nobetci_logs() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" logs -f
}

nobetci_cli() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" exec -e CLI_PROG_NAME="nobetci cli" nobetci python /app/cli.py "$@"
}


update_nobetci_script() {
    colorized_echo blue "Updating nöbetci script"
    curl -sSL $SCRIPT_URL | install -m 755 /dev/stdin /usr/local/bin/nobetci
    colorized_echo green "nöbetci script updated successfully"
}

update_nobetci() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" pull
}

is_nobetci_installed() {
    if [ -d $CONFIG_DIR ]; then
        return 0
    else
        return 1
    fi
}

is_nobetci_up() {
    if [ -z "$($COMPOSE -f $COMPOSE_FILE ps -q -a)" ]; then
        return 1
    else
        return 0
    fi
}

get_panel_address(){
    read -p "Enter the panel address: " PANEL_ADDRESS

    if grep -q "^PANEL_ADDRESS=" "$ENV_FILE"; then
        sed -i.bak "s|^PANEL_ADDRESS=.*|PANEL_ADDRESS=$PANEL_ADDRESS|" "$ENV_FILE"
    else
        echo "PANEL_ADDRESS=$PANEL_ADDRESS" >> "$ENV_FILE"
    fi
}

get_panel_user(){
    read -p "Enter the panel user: " PANEL_USER

    if grep -q "^PANEL_USERNAME=" "$ENV_FILE"; then
        sed -i.bak "s|^PANEL_USERNAME=.*|PANEL_USERNAME=$PANEL_USER|" "$ENV_FILE"
    else
        echo "PANEL_USERNAME=$PANEL_USER" >> "$ENV_FILE"
    fi
}

get_panel_password(){
    read -p "Enter the panel password: " PANEL_PASSWORD

    if grep -q "^PANEL_PASSWORD=" "$ENV_FILE"; then
        sed -i.bak "s|^PANEL_PASSWORD=.*|PANEL_PASSWORD=$PANEL_PASSWORD|" "$ENV_FILE"
    else
        echo "PANEL_PASSWORD=$PANEL_PASSWORD" >> "$ENV_FILE"
    fi
}

get_panel_type() {
    while true; do
        read -p "Enter the panel type (marzneshin, rebecca, marzban): " PANEL_TYPE

        case "$PANEL_TYPE" in
            marzneshin|rebecca|marzban)
                break ;;
            *)
                echo "Invalid panel type. Please enter either 'marzneshin' or 'rebecca' or 'marzban'."
                ;;
        esac
    done

    if grep -q "^PANEL_TYPE=" "$ENV_FILE"; then
        sed -i.bak "s|^PANEL_TYPE=.*|PANEL_TYPE=$PANEL_TYPE|" "$ENV_FILE"
    else
        echo "PANEL_TYPE=$PANEL_TYPE" >> "$ENV_FILE"
    fi
}

get_panel_sync() {
    while true; do
        read -p "Are you want sync Nöbetci with panel?(only available on rebecca) (y/n): " ANSWER

        case "$ANSWER" in
            y|Y)
                SYNC_WITH_PANEL="True"
                break
                ;;
            n|N)
                SYNC_WITH_PANEL="False"
                break
                ;;
            *)
                echo "Invalid input. Please enter y or n."
                ;;
        esac
    done

    if grep -q "^SYNC_WITH_PANEL=" "$ENV_FILE"; then
        sed -i.bak "s|^SYNC_WITH_PANEL=.*|SYNC_WITH_PANEL=$SYNC_WITH_PANEL|" "$ENV_FILE"
    else
        echo "SYNC_WITH_PANEL=$SYNC_WITH_PANEL" >> "$ENV_FILE"
    fi

    echo "SYNC_WITH_PANEL set to $SYNC_WITH_PANEL"
}

set_default_limit() {
    local new_limit="$1"

    if [ -z "$new_limit" ]; then
        echo "Error: No limit value provided to set_default_limit."
        echo "Usage: set_default_limit <NUMBER>"
        return 1
    fi

    if ! [[ "$new_limit" =~ ^[0-9]+$ ]]; then
        echo "Error: Limit value '$new_limit' is not a valid number."
        return 1
    fi


    if grep -q "^DEFAULT_LIMIT=" "$ENV_FILE"; then
        sed -i.bak "s|^DEFAULT_LIMIT=.*|DEFAULT_LIMIT=$new_limit|" "$ENV_FILE"
        echo "Updated existing DEFAULT_LIMIT in $ENV_FILE"
    else
        echo "DEFAULT_LIMIT=$new_limit" >> "$ENV_FILE"
        echo "Added new DEFAULT_LIMIT to $ENV_FILE"
    fi

    echo "DEFAULT_LIMIT set to $new_limit"
}

install_command() {
    check_running_as_root
    # Check if nobetci is already installed
    if is_nobetci_installed; then
        colorized_echo red "Nöbetci is already installed at $CONFIG_DIR"
        read -p "Do you want to override the previous installation? (y/n) "
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            colorized_echo red "Aborted installation"
            exit 1
        fi
    fi
    detect_os
    if ! command -v jq >/dev/null 2>&1; then
        install_package jq
    fi
    if ! command -v curl >/dev/null 2>&1; then
        install_package curl
    fi
    if ! command -v docker >/dev/null 2>&1; then
        install_docker
    fi
	
    database="sqlite"
	nightly=false
 
	while [[ "$#" -gt 0 ]]; do
	    case $1 in
	        -d|--database)
		 		database="$2"
				if [[ ! $database =~ ^(sqlite|mariadb|mysql)$ ]]; then
				    echo "database could only be sqlite, mysql and mariadb."
					exit 1
				fi
	            shift
	            ;;
			-n|--nightly)
	            nightly=true
	            ;;
	        *)
	            echo "Unknown option: $1"
	            exit 1
	            ;;
	    esac
	    shift
	done

    detect_compose
    install_nobetci_script
    install_nobetci $database $nightly

    get_panel_address
    get_panel_user
    get_panel_password
    get_panel_type
    
    if [ "$PANEL_TYPE" = "rebecca" ]; then
        get_panel_sync
        set_default_limit 0
    fi
    
    up_nobetci
    follow_nobetci_logs
}

uninstall_command() {
    check_running_as_root
    # Check if nobetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci's not installed!"
        exit 1
    fi

    read -p "Do you really want to uninstall Nöbetci? (y/n) "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        colorized_echo red "Aborted"
        exit 1
    fi

    detect_compose
    if is_nobetci_up; then
        down_nobetci
    fi
    uninstall_nobetci_script
    uninstall_nobetci
    uninstall_nobetci_docker_images

    read -p "Do you want to remove nöbetci data files too ($DATA_DIR)? (y/n) "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        colorized_echo green "Nöbetci uninstalled successfully"
    else
        uninstall_nobetci_data_files
        colorized_echo green "Nöbetci uninstalled successfully"
    fi
}

up_command() {
    help() {
        colorized_echo red "Usage: $0 up [options]"
        echo ""
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-logs     do not follow logs after starting"
    }

    local no_logs=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-logs)
                no_logs=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci is not installed!"
        exit 1
    fi

    detect_compose

    if is_nobetci_up; then
        colorized_echo red "Nöbetci is already up"
        exit 1
    fi

    up_nobetci
    if [ "$no_logs" = false ]; then
        follow_nobetci_logs
    fi
}

down_command() {

    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci's not installed!"
        exit 1
    fi

    detect_compose

    if ! is_nobetci_up; then
        colorized_echo red "Nöbetci's already down"
        exit 1
    fi

    down_nobetci
}

restart_command() {
    help() {
        colorized_echo red "Usage: $0 restart [options]"
        echo
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-logs     do not follow logs after starting"
    }

    local no_logs=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-logs)
                no_logs=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci's not installed!"
        exit 1
    fi

    detect_compose

    down_nobetci
    up_nobetci
    if [ "$no_logs" = false ]; then
        follow_nobetci_logs
    fi
}

status_command() {

    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        echo -n "Status: "
        colorized_echo red "Not Installed"
        exit 1
    fi

    detect_compose

    if ! is_nobetci_up; then
        echo -n "Status: "
        colorized_echo blue "Down"
        exit 1
    fi

    echo -n "Status: "
    colorized_echo green "Up"

    json=$($COMPOSE -f $COMPOSE_FILE ps -a --format=json)
    services=$(echo "$json" | jq -r 'if type == "array" then .[] else . end | .Service')
    states=$(echo "$json" | jq -r 'if type == "array" then .[] else . end | .State')
    # Print out the service names and statuses
    for i in $(seq 0 $(expr $(echo $services | wc -w) - 1)); do
        service=$(echo $services | cut -d' ' -f $(expr $i + 1))
        state=$(echo $states | cut -d' ' -f $(expr $i + 1))
        echo -n "- $service: "
        if [ "$state" == "running" ]; then
            colorized_echo green $state
        else
            colorized_echo red $state
        fi
    done
}

logs_command() {
    help() {
        colorized_echo red "Usage: nöbetci logs [options]"
        echo ""
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-follow   do not show follow logs"
    }

    local no_follow=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-follow)
                no_follow=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci is not installed!"
        exit 1
    fi

    detect_compose

    if ! is_nobetci_up; then
        colorized_echo red "Nöbetci is not up."
        exit 1
    fi

    if [ "$no_follow" = true ]; then
        show_nobetci_logs
    else
        follow_nobetci_logs
    fi
}

cli_command() {
    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci is not installed!"
        exit 1
    fi

    detect_compose

    if ! is_nobetci_up; then
        colorized_echo red "Nöbetci is not up."
        exit 1
    fi

    nobetci_cli "$@"
}

update_command() {
    check_running_as_root
    # Check if nöbetci is installed
    if ! is_nobetci_installed; then
        colorized_echo red "Nöbetci is not installed!"
        exit 1
    fi

    detect_compose

    update_nobetci_script
    colorized_echo blue "Pulling latest version"
    update_nobetci

    colorized_echo blue "Restarting Nöbetci's services"
    down_nobetci
    up_nobetci

    colorized_echo blue "Nöbetci updated successfully"
}


usage() {
    colorized_echo red "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  up              Start services"
    echo "  down            Stop services"
    echo "  restart         Restart services"
    echo "  status          Show status"
    echo "  logs            Show logs"
    echo "  cli             Nöbetci command-line interface"
    echo "  install         Install Nöbetci"
    echo "  update          Update latest version"
    echo "  uninstall       Uninstall Nöbetci"
    echo "  install-script  Install Nöbetci script"
    echo
}

case "$1" in
    up)
    shift; up_command "$@";;
    down)
    shift; down_command "$@";;
    restart)
    shift; restart_command "$@";;
    status)
    shift; status_command "$@";;
    logs)
    shift; logs_command "$@";;
    cli)
    shift; cli_command "$@";;
    install)
    shift; install_command "$@";;
    update)
    shift; update_command "$@";;
    uninstall)
    shift; uninstall_command "$@";;
    install-script)
    shift; install_nobetci_script "$@";;
    *)
    usage;;
esac
