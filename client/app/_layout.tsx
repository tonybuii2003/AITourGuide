import { Stack } from "expo-router";
import { View, Text, Image } from "react-native";
const HeaderTitle = () => (
  <View style={{ flexDirection: "row", alignItems: "center" }}>
    <Image
      source={require("../assets/images/logo.jpeg")}
      style={{ width: 50, height: 50, resizeMode: "contain", marginRight: 0 }}
    />
    <Text style={{ fontSize: 18, fontWeight: "bold" }}>CuratAI</Text>
  </View>
);
export default function RootLayout() {
  return <Stack 
    screenOptions={{
      headerTitle: HeaderTitle,
    }}
  />;
}
