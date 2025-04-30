// ChatScreen.styles.ts
import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  messagesContainer: {
    flexGrow: 1,
    padding: 10,
  },
  messageContainer: {
    marginVertical: 5,
    paddingRight: 10,
    paddingLeft: 10,
    borderRadius: 20,
    maxWidth: '80%',
  },
  myMessage: {
    backgroundColor: '#dbac59',
    alignSelf: 'flex-end',
  },
  otherMessage: {
    backgroundColor: '#FFF',
    alignSelf: 'flex-start',
  },
  feedbackMessage: {
    backgroundColor: 'lightblue',
    alignSelf: 'flex-start',
  },
  messageText: {
    fontSize: 16,
  },
  messageTime: {
    fontSize: 10,
    textAlign: 'right',
    marginTop: 5,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderColor: '#CCC',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  textInput: {
    flex: 1,
    backgroundColor: '#FFF',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#CCC',
    fontSize: 16,
  },
  sendButton: {
    marginLeft: 10,
    backgroundColor: '#FFB703',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 8,
  },
  sendButtonText: {
    color: '#0',
    fontWeight: 'bold',
  },
});
