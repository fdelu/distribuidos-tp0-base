SERVER_ADDRESS=server 
SERVER_PORT=12345
TEST_MESSAGE="This message will be sent from netcat to the EchoServer"

RED='\033[0;31m'
GREEN='\033[0;32m'

OUTPUT=$(printf "$TEST_MESSAGE" | nc $SERVER_ADDRESS $SERVER_PORT)
if [[ $OUTPUT == $TEST_MESSAGE ]]; then
    echo -e "${GREEN}SUCCESS - server echoed the messaged correctly"
else
    echo -e "${RED}FAILED\n${RED}Message sent: '$TEST_MESSAGE'\n${RED}Actual response: '$OUTPUT'"
    exit 1
fi