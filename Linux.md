# Linux for Beginners

A simple guide to the Linux OS, the terminal, and everyday commands — written for people starting DevOps or learning Linux from scratch.

---

## Table of Contents

1. [What is Linux?](#what-is-linux)
2. [The Terminal & Environment](#the-terminal--environment)
3. [Navigation](#navigation)
4. [File & Directory Management](#file--directory-management)
5. [Viewing & Editing Files](#viewing--editing-files)
6. [Search](#search)
7. [File Permissions & Ownership](#file-permissions--ownership)
8. [System Information](#system-information)
9. [Processes](#processes)
10. [Disk & Memory](#disk--memory)
11. [Networking & Connectivity](#networking--connectivity)
12. [Packages (apt)](#packages-apt)
13. [Services (systemctl)](#services-systemctl)
14. [Archives](#archives)
15. [Pipes & Redirects](#pipes--redirects)
16. [Multipass (Local Linux VMs)](#multipass-local-linux-vms)
17. [SSH Config](#ssh-config)

---

## What is Linux?

**Linux** is an open-source operating system. Servers, cloud VMs, Docker containers, and most DevOps tools run on Linux.

You mostly work with Linux through the **terminal** (command line) — a text window where you type commands instead of clicking buttons.

> Think of Windows Explorer / Finder as the GUI. The terminal is the same computer, controlled with text commands.

### Why DevOps needs Linux

- Production servers are almost always Linux
- Docker images usually base on Linux (Ubuntu, Alpine, Debian)
- CI/CD runners, Kubernetes nodes, and SSH access all use Linux commands

---

## The Terminal & Environment

When you open a terminal, you get a **shell** (often `bash` or `zsh`). The shell reads your commands and talks to the OS.

| Idea | Meaning |
|------|---------|
| **Home directory** | Your personal folder, usually `/home/username` (shortcut: `~`) |
| **Path** | Full location of a file, e.g. `/var/log/nginx/error.log` |
| **Absolute path** | Starts from root `/` — always the same place |
| **Relative path** | Relative to where you are now (e.g. `./app`, `../logs`) |
| **Root `/`** | Top of the filesystem tree |
| **Root user** | Superuser (admin). Use carefully with `sudo` |
| **Environment variables** | Settings the shell knows, e.g. `$HOME`, `$PATH` |

```bash
echo $HOME          # print your home directory
echo $PATH          # folders where the shell looks for commands
whoami              # current username
```

**`whoami`** — Prints the username of the current user.

**`sudo`** — Runs a command with admin (root) privileges. Needed for installs, services, and system files.

```bash
sudo apt update
```

---

## Navigation

**`pwd`** — Prints the full path of your current working directory (where you are right now).

```bash
pwd
```

**`cd`** — Changes your current directory.

```bash
cd /var/log          # go to /var/log
cd ~                 # go to home
cd ..                # go one level up
cd -                 # go back to previous directory
```

**`ls`** — Lists files and directories in the current folder.

```bash
ls                   # basic list
ls -l                # long list (permissions, size, date)
ls -a                # include hidden files (names starting with .)
ls -lah              # long + all + human-readable sizes
```

---

## File & Directory Management

**`touch`** — Creates a new empty file, or updates the timestamp if the file already exists.

```bash
touch notes.txt
```

**`mkdir`** — Creates a new directory (folder).

```bash
mkdir new_folder
mkdir -p projects/app/src   # create nested folders in one go
```

**`rmdir`** — Removes an **empty** directory only.

```bash
rmdir empty_folder
```

**`rm`** — Deletes files. Use carefully — deleted files do not go to a recycle bin.

```bash
rm file.txt              # delete a file
rm -r folder             # delete a directory and its contents
rm -rf folder            # force delete (no prompts) — be very careful
```

**`cp`** — Copies files or directories from one place to another.

```bash
cp source.txt dest.txt
cp file.txt /home/ubuntu/
cp -r source_dir/ dest_dir/    # copy a directory recursively
```

**`mv`** — Moves a file/folder, or renames it.

```bash
mv old.txt new.txt              # rename
mv file.txt /home/ubuntu/docs/  # move
```

---

## Viewing & Editing Files

**`cat`** — Prints the entire file contents to the screen. Best for short files.

```bash
cat filename
```

**`less`** — Opens a file for interactive viewing. Scroll with arrows; press `q` to quit.

```bash
less /var/log/syslog
```

**`head`** — Shows the first lines of a file (default: 10).

```bash
head filename
head -n 20 filename
```

**`tail`** — Shows the last lines of a file (default: 10). Useful for logs.

```bash
tail filename
tail -n 50 filename
tail -f /var/log/nginx/access.log   # follow live updates
```

**`nano`** — Simple beginner-friendly text editor in the terminal.

```bash
nano filename
# Ctrl+O save, Ctrl+X exit
```

**`vim`** — Powerful text editor (steeper learning curve). Press `i` to insert, `Esc` then `:wq` to save and quit, or `:q!` to quit without saving.

```bash
vim filename
```

---

## Search

**`grep`** — Finds and prints lines that contain a search term in a file (or many files).

```bash
grep "error" filename
grep -i "error" filename          # case-insensitive
grep -r "TODO" ./src              # search recursively in a folder
```

**`find`** — Searches for files and directories by name, type, or other rules.

```bash
find . -name "*.log"              # logs in current tree
find /var -type d -name "nginx"   # directories named nginx under /var
```

---

## File Permissions & Ownership

Every file has an **owner**, a **group**, and **permissions** (read / write / execute).

View them with:

```bash
ls -l
```

Example output idea: `-rw-r--r--  1 ubuntu ubuntu  120 Jul 29 notes.txt`

**`chmod`** — Changes file permissions (who can read, write, or execute).

```bash
chmod 755 script.sh     # owner: rwx, group/others: r-x
chmod +x script.sh      # make a file executable
```

**`chown`** — Changes the user and/or group ownership of a file or folder.

```bash
sudo chown ubuntu:ubuntu file.txt
sudo chown -R ubuntu:ubuntu /var/www/app
```

**`passwd`** — Changes the password for a user account.

```bash
passwd                  # change your own password
sudo passwd ubuntu      # change another user's password (as admin)
```

---

## System Information

**`uname`** — Shows core system / kernel information.

```bash
uname -a                # full details (kernel, arch, etc.)
```

**`hostname`** — Shows (or sets) the computer’s network name.

```bash
hostname
```

**`uptime`** — How long the system has been running, plus load averages.

```bash
uptime
```

**`free`** — Shows total, used, and available RAM and swap.

```bash
free -h                 # human-readable (MB/GB)
```

**`df`** — Shows disk space usage for mounted filesystems.

```bash
df -h
```

**`du`** — Shows how much space a folder/file uses.

```bash
du -sh /var/log         # summary for one path
du -h --max-depth=1 .   # size of each item in current folder
```

---

## Processes

A **process** is a running program.

**`ps`** — Lists running processes.

```bash
ps                      # basic
ps aux                  # detailed list of all processes
```

**`top`** / **`htop`** — Live view of CPU and memory usage by process. Press `q` to quit. (`htop` is nicer if installed.)

```bash
top
htop
```

**`kill`** — Stops a process by its PID (process ID).

```bash
kill 1234
kill -9 1234            # force kill
```

Useful monitors (install with apt):

```bash
sudo apt install iftop atop
```

**`iftop`** — Live view of network bandwidth by connection.  
**`atop`** — Advanced system/process monitor (CPU, disk, network over time).

---

## Disk & Memory

Quick recap of the commands you’ll use most:

```bash
free -h     # RAM
df -h       # disk free space
du -sh *    # size of items in current directory
```

---

## Networking & Connectivity

**`ping`** — Sends packets to a host to test if it is reachable.

```bash
ping google.com
ping -c 4 8.8.8.8       # stop after 4 packets
```

**`curl`** — Talks to URLs from the terminal (download content, test APIs).

```bash
curl https://google.com
curl -s https://google.com          # silent (less noise)
curl -I https://example.com         # headers only
```

**`wget`** — Downloads files from the web.

```bash
wget https://example.com/file.zip
wget -qO- https://google.com        # quiet, print to screen
```

**`ip`** / **`ifconfig`** — Shows network interfaces and IP addresses. Prefer `ip` on modern Linux.

```bash
ip a                    # addresses
ip link                 # interfaces
ifconfig                # older style (may need net-tools package)
```

**`ssh`** — Connects securely to a remote Linux machine.

```bash
ssh ubuntu@192.168.1.10
ssh devops-vm           # if configured in ~/.ssh/config
```

---

## Packages (apt)

On Ubuntu / Debian, **`apt`** installs and updates software.

```bash
sudo apt update                     # refresh package lists
sudo apt upgrade                    # upgrade installed packages
sudo apt install nginx              # install a package
sudo apt install iftop atop         # install multiple packages
sudo apt remove nginx               # remove a package
sudo apt search keyword             # search package names
```

**`apt update`** — Downloads the latest list of available packages (does not install them yet).  
**`apt install`** — Installs software from the package repository.  
**`apt remove`** — Uninstalls a package.

---

## Services (systemctl)

**systemd** manages background services (nginx, docker, ssh, etc.).

**`systemctl`** — Start, stop, restart, enable, and check service status.

```bash
sudo systemctl status nginx         # is nginx running?
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl enable nginx         # start on boot
sudo systemctl disable nginx        # do not start on boot
sudo systemctl reload nginx         # reload config without full restart
```

**`journalctl`** — Views logs collected by systemd.

```bash
journalctl -u nginx                 # logs for nginx service
journalctl -u nginx -f              # follow live
```

---

## Archives

**`tar`** — Creates or extracts archive files (often with gzip compression).

```bash
tar -czvf backup.tar.gz folder/     # create compressed archive
tar -xzvf backup.tar.gz             # extract
```

**`zip`** / **`unzip`** — Zip format create / extract.

```bash
zip -r archive.zip folder/
unzip archive.zip
```

---

## Pipes & Redirects

These let you combine commands and save output — very common in real work.

**Pipe `|`** — Sends output of one command into the next.

```bash
ps aux | grep nginx
cat file.log | grep "error"
```

**Redirect `>`** — Writes command output to a file (overwrites).

```bash
echo "hello" > notes.txt
```

**Redirect `>>`** — Appends to a file (does not overwrite).

```bash
echo "another line" >> notes.txt
```

**Redirect `<`** — Feeds a file as input to a command.

```bash
sort < names.txt
```

---

## Multipass (Local Linux VMs)

[Multipass](https://multipass.run/) runs Ubuntu VMs on your laptop — great for practicing Linux without a cloud server.

```bash
multipass list                          # list all VMs
multipass shell <instance_name>         # open a shell inside the VM
multipass start <instance_name>         # start a stopped VM
multipass stop <instance_name>          # stop a running VM
multipass delete <instance_name>        # delete (soft delete)
multipass purge                         # permanently remove deleted VMs
```

### Fresh VM example

```bash
# 1. Delete an old VM (example name)
multipass delete deserving-walleye

# 2. Purge it completely
multipass purge

# 3. Create a fresh VM
multipass launch --name devops-vm --disk 20G --memory 2G --cpus 2

# 4. Enter the VM
multipass shell devops-vm
```

---

## SSH Config

Store host shortcuts in `~/.ssh/config` so you can type short names instead of long `ssh` commands.

```bash
# ~/.ssh/config

Host production
    HostName 64.23.145.12
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519

Host staging
    HostName 64.23.145.13
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519

Host devops-vm
    HostName 192.168.252.9
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
```

Then connect with:

```bash
ssh devops-vm
ssh staging
ssh production
```

For Multipass VMs you can also use:

```bash
multipass shell devops-vm
```

---

## Quick Cheatsheet

| Need | Command |
|------|---------|
| Where am I? | `pwd` |
| List files | `ls -lah` |
| Change folder | `cd path` |
| Make folder | `mkdir name` |
| Create file | `touch file` |
| Read file | `cat` / `less` |
| Find text | `grep "text" file` |
| Copy / move / delete | `cp` / `mv` / `rm` |
| Permissions | `chmod` / `chown` |
| Disk / RAM | `df -h` / `free -h` |
| Processes | `ps aux` / `top` |
| Install software | `sudo apt install ...` |
| Service status | `sudo systemctl status ...` |
| Remote login | `ssh host` |
