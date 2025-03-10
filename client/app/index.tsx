import React from "react";
import { SafeAreaView, StyleSheet } from "react-native";
import ChatScreen from "./pages/chatPage";
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function Index() {
  return (
    <GestureHandlerRootView style={styles.container}>
      <ChatScreen />
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
