// app/_layout.tsx
import React from "react";
import { Stack } from "expo-router";
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import { useRouter, useSegments, Redirect } from "expo-router";

function HeaderTitle() {
  const router = useRouter();
  return (
    <TouchableOpacity
      style={styles.titleContainer}
      onPress={() => router.push("/")}
    >
      <Image
        source={require("../assets/images/logo.jpeg")}
        style={styles.logo}
      />
      <Text style={styles.titleText}>CuratAI</Text>
    </TouchableOpacity>
  );
}

export default function RootLayout() {
  const router = useRouter();
  const segments = useSegments();

  // If we're on any sub‐route (length > 1), immediately redirect back to "/"
  if (segments.length > 1) {
    return <Redirect href="/" />;
  }

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
  titleContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  logo: {
    width: 50,
    height: 50,
    resizeMode: "contain",
    marginRight: 8,
  },
  titleText: {
    fontSize: 18,
    fontWeight: "bold",
  },
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
