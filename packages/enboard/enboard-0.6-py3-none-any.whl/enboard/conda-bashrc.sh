if [[ -f /etc/bash.bashrc ]]; then
  source /etc/bash.bashrc
fi
if [[ -f ~/.bashrc ]]; then
  source ~/.bashrc
fi

activate_cmds="$(PS1=$PS1 conda shell.posix activate ${CONDA_PREFIX})"
\eval "$activate_cmds"
