import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: "#0f1115" },
          headerTintColor: "#e8eaed",
          contentStyle: { backgroundColor: "#0f1115" },
        }}
      >
        <Stack.Screen name="index" options={{ title: "完善宠物信息" }} />
        <Stack.Screen name="home" options={{ title: "Any-Family 🐾" }} />
      </Stack>
    </SafeAreaProvider>
  );
}
