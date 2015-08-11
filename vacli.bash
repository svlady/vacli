#!/usr/bin/env bash

# -------------------------------------------------------------------------------
#
#    PROPRIETARY/CONFIDENTIAL
#    Copyright (c) 2015 Verizon, All Rights Reserved.
#    Not for disclosure without written permission.
#
#    Author:  Vyacheslav Vladyshevsky (vyacheslav.vladyshevsky@intl.verizon.com)
#    Project: Verizon Cloud Automation
#
#    Bash auto-completion for vacli tool
#
#    Far better idea would be to implement complete state matrix, however, this
#    quick-hack function does the trick for the most part of the time.
#
# -------------------------------------------------------------------------------

_vacli()
{
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    #
    #  Global CLI options that we will auto-complete if no command provided
    #
    glob_args="--api-access-key --api-account --api-cloud-space --api-endpoint --api-secret-key \
        --log-file --log-level --config-file --profile"

    #
    #  Basic CLI commands we'll complete. Note leading and trailing spaces
    #  in the following string. They needed to distinguish commands possibly
    #  starting or ending with the same sub-string
    #
    commands=" get delete options patch post put get-root get-admin-root get-resource-groups job-list job-poll \
        fw-acl-list fw-acl-add fw-acl-del public-ip-list public-ip-add public-ip-del list-vdisk-templates \
        list-vm-templates list-vdisks list-vnets list-vms list-vnics vdisk-create vdisk-edit vnet-create \
        vnet-edit vm-create vm-edit vm-add-vnic vm-add-vdisk vm-list-mounts vnic-edit update-iops vm-ctl "

    #
    # Looking for known CLI commands in the command line, so that we will
    # auto-complete options corresponding and valid for this command only
    #
    cmd=""
    for word in ${COMP_WORDS[@]}; do
        if [[ ${commands} =~ " ${word} " ]] ; then
            cmd=${word}
            break
        fi
    done

    #
    #  Auto-complete arguments for the CLI command
    #
    if [[ ${cmd} && ${cur} != ${cmd} ]] ; then
        #
        #  Suggest the choice for command arguments with known options
        #
        if [[ ${prev} == -* ]] ; then
            case "${prev}" in
                --json-file)
                    COMPREPLY=( $(compgen -f -- ${cur}) )
                    return 0
                    ;;
                --ip)
                    args=$(./vacli public-ip-list --table address | sed 1d) ;;
                --proto)
                    args="TCP UDP ICMP ESP ALL" ;;
                --action)
                    args="DISCARD REJECT ACCEPT" ;;
                --cmd)
                    args="reboot reset shutdown power-on power-off" ;;
                *)
                    args="" ;;
            esac
            if [[ ${args} ]] ; then
                COMPREPLY=( $(compgen -W "${args}" -- ${cur}) )
                return 0
            fi
        fi

        #
        #  Suggesting context specific command arguments, if command has been provided in the command line
        #
        case "${cmd}" in
            get|delete|options)
                args="--href --headers" ;;
            patch|post|put)
                args="--href --headers --json-file --dry-run" ;;
            get-resource-groups)
                args="--table" ;;
            job-list)
                args="--last --table" ;;
            job-poll)
                args="--job --timeout --poll-interval --table" ;;
            fw-acl-list)
                args="--ip --ip-ref --table" ;;
            fw-acl-add)
                args="--ip --ip-ref --idx --proto --action --src-cidr --src-port --dst-cidr --dst-port --dry-run" ;;
            fw-acl-del)
                args="--ip --ip-ref --idx --all --dry-run" ;;
            public-ip-list)
                args="--tag --with-vms --table" ;;
            public-ip-add)
                args="--tags --name --wait --dry-run" ;;
            public-ip-del)
                args="--ip --ip-ref --dry-run" ;;
            public-ip-list)
                args="--tag --with-vms --table" ;;
            list-vdisk-templates|list-vm-templates)
                args="--table" ;;
            list-vdisks|list-vnets|list-vms)
                args="--tag --table" ;;
            list-vnics)
                args="--vm --vnet --table" ;;
            vdisk-create)
                args="--name --description --tags --size --from-template --from-snapshot --fault-tolerance --wait --dry-run" ;;
            vdisk-edit)
                args="--vdisk --name --tags --description" ;;
            vnet-create)
                args="--name --description --tags --cidr --wait --dry-run" ;;
#            vnet-edit)
#                args="--vnet --name --tags --description" ;;
            vm-create)
                args="--name --description --tags --cpus --cpu-speed --memory --iops --vdisks --vdisk-template \
                    --public-ip --vnets --bandwidth --guest-options --wait --dry-run" ;;
#            vm-edit)
#                args="--vm --name --tags --description" ;;
            vm-add-vnic)
                args="--vm --vnet --ipv4 --description --public-ip --bandwidth --wait --dry-run" ;;
            vm-add-vdisk)
                args="--vm --vdisk --iops --boot --wait --dry-run" ;;
            vm-list-mounts)
                args="--vm --table" ;;
#            vnic-edit)
#                args="--vnic --vnet --ipv4 --description --public-ip --bandwidth --wait --dry-run" ;;
            update-iops)
                args="--vdisk-mount --iops" ;;
            vm-ctl)
                args="--vm --cmd --force --wait" ;;
            *)
                args=${glob_args} ;;
        esac

        COMPREPLY=( $(compgen -W "${args}" -- ${cur}) )
        return 0
    elif [[ ${prev} == -* ]] ; then
        #
        #  Complete the choice for global arguments with known options.
        #
        case "${prev}" in
            --log-level)
                args="critical error warning info debug" ;;
            --profile)
                args="default" ;;
            --config-file)
                COMPREPLY=( $(compgen -f -- ${cur}) )
                return 0
                ;;
            *)
                args=${glob_args} ;;
        esac
        COMPREPLY=( $(compgen -W "${args}" -- ${cur}) )
        return 0
    fi

    if [[ ${cur} == -* ]] ; then
        args=${glob_args}
    else
        args=${commands}
    fi

    COMPREPLY=($(compgen -W "${args}" -- ${cur}))
    return 0
}

complete -F _vacli vacli
