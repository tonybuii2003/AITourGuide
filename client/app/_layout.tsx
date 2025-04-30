// app/_layout.tsx
import React from "react";
import { Stack } from "expo-router";
import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

const HeaderTitle = () => (
  <View style={{ flexDirection: "row", alignItems: "center" }}>
    <Image
      source={require("../assets/images/logo.jpeg")}
      style={{ width: 50, height: 50, resizeMode: "contain", marginRight: 8 }}
    />
    <Text style={{ fontSize: 18, fontWeight: "bold" }}>CuratAI</Text>
  </View>
);

export default function RootLayout() {
  const router = useRouter();

  return (
    <Stack
      screenOptions={{
        headerTitle: HeaderTitle,
        headerRight: () => (
          <TouchableOpacity
            onPress={() => router.push("/record")}
            style={styles.boxButton}
          >
            <Text style={styles.boxButtonText}>Voice Assistant (beta)</Text>
          </TouchableOpacity>
        ),
      }}
    />
  );
}

const styles = StyleSheet.create({
  boxButton: {
    marginRight: 16,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: "#FFB703",
    borderRadius: 6,
  },
  boxButtonText: {
    fontSize: 16,
    color: "#FFB703",
    fontWeight: "500",
  },
});
