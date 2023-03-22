# ssh without password
# Optional if already existed
ssh-keygen -t rsa
ssh b@B mkdir -p .ssh

# Required
cat .ssh/id_rsa.pub | ssh b@B 'cat >> .ssh/authorized_keys'
