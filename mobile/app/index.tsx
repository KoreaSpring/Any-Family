import { useRouter } from "expo-router";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { api, PetProfile } from "@/lib/api";
import { C } from "@/lib/theme";

/** 引导录入：低摩擦采集品种先验 + 个体基础所需信息。 */
export default function Onboarding() {
  const router = useRouter();
  const [name, setName] = useState("Lucky");
  const [species, setSpecies] = useState<"dog" | "cat">("dog");
  const [breed, setBreed] = useState("golden_retriever");
  const [age, setAge] = useState("3");
  const [commands, setCommands] = useState("sit, come, wait");
  const [toys, setToys] = useState("laser, ball");
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit() {
    setSaving(true);
    setErr(null);
    try {
      const patch: Partial<PetProfile> = {
        name: name.trim(),
        species,
        breed: breed.trim() || null,
        age: Number(age) || null,
        trained_commands: commands.split(",").map((s) => s.trim()).filter(Boolean),
        preferences: { toys: toys.split(",").map((s) => s.trim()).filter(Boolean) },
      };
      await api.updatePet(patch);
      router.replace("/home");
    } catch (e) {
      setErr(`保存失败，请确认服务端已启动（${api.baseUrl}）。`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <ScrollView style={{ backgroundColor: C.bg }} contentContainerStyle={s.wrap}>
      <Text style={s.lead}>先让 Agent 认识你的宝贝</Text>
      <Text style={s.hint}>
        品种等信息用于"冷启动"解读（品种先验），后续会被这只宠物的真实观测逐步校准。
      </Text>

      <Field label="名字">
        <TextInput style={s.input} value={name} onChangeText={setName} placeholder="它叫什么" placeholderTextColor={C.mut} />
      </Field>

      <Field label="物种">
        <View style={s.row}>
          {(["dog", "cat"] as const).map((sp) => (
            <Pressable
              key={sp}
              style={[s.choice, species === sp && s.choiceOn]}
              onPress={() => setSpecies(sp)}
            >
              <Text style={[s.choiceTxt, species === sp && s.choiceTxtOn]}>
                {sp === "dog" ? "🐕 狗" : "🐈 猫"}
              </Text>
            </Pressable>
          ))}
        </View>
      </Field>

      <Field label="品种">
        <TextInput style={s.input} value={breed} onChangeText={setBreed} placeholder="如 golden_retriever" placeholderTextColor={C.mut} />
      </Field>

      <Field label="年龄（岁）">
        <TextInput style={s.input} value={age} onChangeText={setAge} keyboardType="numeric" placeholderTextColor={C.mut} />
      </Field>

      <Field label="已训练指令（逗号分隔，用于「看到我」）">
        <TextInput style={s.input} value={commands} onChangeText={setCommands} placeholderTextColor={C.mut} />
      </Field>

      <Field label="喜欢的玩具（逗号分隔）">
        <TextInput style={s.input} value={toys} onChangeText={setToys} placeholderTextColor={C.mut} />
      </Field>

      {err && <Text style={s.err}>{err}</Text>}

      <Pressable style={s.btn} onPress={submit} disabled={saving}>
        {saving ? <ActivityIndicator color="#06243a" /> : <Text style={s.btnTxt}>完成，进入首页</Text>}
      </Pressable>
    </ScrollView>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={{ marginBottom: 14 }}>
      <Text style={s.label}>{label}</Text>
      {children}
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { padding: 20, paddingBottom: 48 },
  lead: { color: C.txt, fontSize: 22, fontWeight: "700", marginBottom: 6 },
  hint: { color: C.mut, fontSize: 13, marginBottom: 20, lineHeight: 19 },
  label: { color: C.mut, fontSize: 13, marginBottom: 6 },
  input: {
    backgroundColor: C.card2, color: C.txt, borderRadius: 10, borderWidth: 1,
    borderColor: C.line, paddingHorizontal: 12, paddingVertical: 11, fontSize: 15,
  },
  row: { flexDirection: "row", gap: 10 },
  choice: {
    flex: 1, backgroundColor: C.card2, borderRadius: 10, borderWidth: 1, borderColor: C.line,
    paddingVertical: 12, alignItems: "center",
  },
  choiceOn: { borderColor: C.acc },
  choiceTxt: { color: C.txt, fontSize: 15 },
  choiceTxtOn: { color: C.acc, fontWeight: "700" },
  btn: {
    backgroundColor: C.acc, borderRadius: 12, paddingVertical: 15, alignItems: "center",
    marginTop: 10,
  },
  btnTxt: { color: "#06243a", fontSize: 16, fontWeight: "700" },
  err: { color: C.urgent, fontSize: 13, marginBottom: 10 },
});
