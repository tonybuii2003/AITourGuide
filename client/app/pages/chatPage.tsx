import React, { useState, useRef, useEffect } from 'react';
import {
  ListRenderItem,
  Text,
  View,
  TextInput,
  Platform,
  KeyboardAvoidingView,
  Linking,
  TouchableOpacity,
} from 'react-native';
import { FlatList as RNFlatList } from 'react-native-gesture-handler';
import Markdown from 'react-native-markdown-display';
import { DotIndicator } from 'react-native-indicators';
import { styles } from '../stylesheets/ChatScreen.styles';

interface ChatMessage {
  id: number;
  text: string;
  createdAt: string;
  user: 'Me' | 'Bot';
  feedback?: boolean;
}

const ChatScreen: React.FC = () => {
  const [message, setMessage] = useState<ChatMessage[]>([
    {
      id: 1,
      text: `Welcome! I'm your personal curator. Ask any question about The Met.`,
      createdAt: new Date().toLocaleTimeString(),
      user: 'Bot',
    },
  ]);
  const [text, setText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [questionCount, setQuestionCount] = useState<number>(0);

  const flatListRef = useRef<RNFlatList<ChatMessage>>(null);
  const botIdRef = useRef<number>(-1);

  useEffect(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, [message]);

  const handleSend = (): void => {
    if (!text.trim()) return;

    // 1️⃣ Add the user's message
    const trimmed = text.trim();
    setMessage(prev => [
      ...prev,
      {
        id: prev.length + 1,
        text: trimmed,
        createdAt: new Date().toLocaleTimeString(),
        user: 'Me',
      },
    ]);
    setText('');

    // 2️⃣ Track question count & show loader
    const nextCount = questionCount + 1;
    setQuestionCount(nextCount);
    setLoading(true);

    // 3️⃣ Add an empty Bot placeholder and store its id in a ref
    setMessage(prev => {
      const newBotId = prev.length + 1;
      botIdRef.current = newBotId;
      return [
        ...prev,
        {
          id: newBotId,
          text: '',
          createdAt: new Date().toLocaleTimeString(),
          user: 'Bot',
        },
      ];
    });

    // 4️⃣ Fire off a POST‐SSE XHR
    const xhr = new XMLHttpRequest();
    const url = 'https://007dc339a8f4.ngrok.app/api/rag/stream';
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Accept', 'text/event-stream');
    xhr.setRequestHeader('Content-Type', 'application/json');

    let lastIndex = 0;
    let buffer = '';
    let accumulated = '';

    xhr.onprogress = () => {
      const chunk = xhr.responseText.slice(lastIndex);
      lastIndex = xhr.responseText.length;
      buffer += chunk;

      const parts = buffer.split('\n\n');
      parts.slice(0, -1).forEach(event => {
        event.split('\n').forEach(line => {
          if (line.startsWith('data:')) {
            const data = line.replace(/^data:\s*/, '');
            if (accumulated === '') {
              setLoading(false);
            }    
            accumulated += data;
            setMessage(prev => {
              const copy = [...prev];
              const idx = copy.findIndex(m => m.id === botIdRef.current);
              if (idx !== -1) copy[idx].text = accumulated;
              return copy;
            });
          }
        });
      });
      buffer = parts[parts.length - 1];
    };

    xhr.onloadend = () => {
      setLoading(false);
      if (nextCount === 3) {
        setMessage(prev => [
          ...prev,
          {
            id: prev.length + 1,
            text:
              "From Tony (Founding Engineer): I hope you enjoy CuratAI! How's the experience? Please provide your feedback here: https://forms.gle/axCVoVievgbC2NMZ9",
            createdAt: new Date().toLocaleTimeString(),
            user: 'Bot',
            feedback: true,
          },
        ]);
      }
    };

    xhr.onerror = () => {
      setLoading(false);
      console.error('Stream error', xhr.statusText);
    };

    // kick it off
    xhr.send(JSON.stringify({ query: trimmed }));
  };

  const renderItem: ListRenderItem<ChatMessage> = ({ item }) => {
    if (item.user === 'Bot' && !item.feedback && item.text.trim() === '') {
      return null;
    }
    if (item.feedback) {
      const link = 'https://forms.gle/axCVoVievgbC2NMZ9';
      return (
        <View
          style={[
            styles.messageContainer,
            item.user === 'Me' ? styles.myMessage : styles.otherMessage,
            styles.feedbackMessage,
          ]}
        >
          <Text style={styles.messageText}>
            From Tony (Founding Engineer): I hope you enjoy CuratAI! How's the
            experience? Please provide your feedback here:{' '}
            <Text
              style={{ color: 'blue', textDecorationLine: 'underline' }}
              onPress={() => Linking.openURL(link)}
            >
              {link}
            </Text>
          </Text>
          <Text style={styles.messageTime}>{item.createdAt}</Text>
        </View>
      );
    }

    return (
      <View
        style={[
          styles.messageContainer,
          item.user === 'Me' ? styles.myMessage : styles.otherMessage,
        ]}
      >
        <Markdown style={{ body: { fontSize: 16 } }}>
          {item.text}
        </Markdown>
        <Text style={styles.messageTime}>{item.createdAt}</Text>
      </View>
    );
  };

  const renderFooter = () => (
    <View style={{ padding: 10, alignItems: 'flex-start', opacity: loading ? 1 : 0 }}>
      <DotIndicator animating={true} count={3} size={6} hidesWhenStopped={true} />
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <RNFlatList
        ref={flatListRef}
        data={message}
        renderItem={renderItem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.messagesContainer}
        ListFooterComponent={renderFooter}
      />

      <View style={styles.inputContainer}>
        <TextInput
          style={[styles.textInput, loading && { color: 'gray' }]}
          placeholder="Type your message"
          value={text}
          onChangeText={setText}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          editable={!loading}
          selectTextOnFocus={!loading}
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
          <Text style={styles.sendButtonText}>{loading ? '...' : 'Send'}</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

export default ChatScreen;
