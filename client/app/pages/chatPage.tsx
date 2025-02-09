import React, {useState} from 'react';

import { ListRenderItem, Text, View, TextInput, Platform, KeyboardAvoidingView, TouchableOpacity  } from 'react-native';
import axios from 'axios';
import { styles } from '../stylesheets/ChatScreen.styles';
import { FlatList } from 'react-native-gesture-handler';
interface ChatMessage {
    id: number;
    text: string;
    createdAt: string;
    user: 'Me' | 'Bot';
}

const ChatScreen: React.FC = () => {
    const [message, setMessage] = useState<ChatMessage[]>([
        {
            id: 1,
            text: 'Welcome! Ask any question about The Met.',
            createdAt: new Date().toLocaleTimeString(),
            user: 'Bot',
          },

    ]);
    const [text, setText] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const sendQuery = async (query: string): Promise<string> => {
        try{
            const response = await axios.post('http://localhost:8080/api/rag', {query})
            return response.data.answer;
        } catch (error) {
            console.error('Error sending query:', error);
            return 'Error connecting to server.';
        }
    }
    const handleSend = async (): Promise<void> => {
        if (text.trim() === '') return;
        const newMessage: ChatMessage = {
            id: message.length + 1,
            text,
            createdAt: new Date().toLocaleTimeString(),
            user: 'Me',
        };
        setMessage((prevMessages) => [...prevMessages, newMessage]);
        setLoading(true);
        const answer = await sendQuery(text);

        const botMessage: ChatMessage = {
            id: message.length+2,
            text:answer,
            createdAt: new Date().toLocaleTimeString(),
            user: 'Bot',
        };
        setMessage((prevMessages) => [...prevMessages, botMessage]);
        setText('');
        setLoading(false);
    };

    const renderItem: ListRenderItem<ChatMessage> = ({ item }) => (
        <View
        style={[
            styles.messageContainer,
            item.user === 'Me' ? styles.myMessage : styles.otherMessage,
          ]}
        >
            <Text style={styles.messageText}>{item.text}</Text>
            <Text style={styles.messageTime}>{item.createdAt}</Text>
        </View>
    );
    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 60 : 0}
        >
            <FlatList
                data={message}
                renderItem={renderItem}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.messagesContainer}
            />

            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.textInput}
                    placeholder="Type your message"
                    value={text}
                    onChangeText={setText}
                    onSubmitEditing={handleSend}
                    returnKeyType="send"
                />
                <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
                    <Text style={styles.sendButtonText}>{loading ? '...' : 'Send'}</Text>
                </TouchableOpacity>
            
            </View>

        </KeyboardAvoidingView>
    );
}
export default ChatScreen;