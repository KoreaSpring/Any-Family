import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  api,
  HealthAlert,
  Interpretation,
  Overview,
  PetProfile,
} from "@/lib/api";
import { C } from "@/lib/theme";

const ACT: Record<string, string> = {
  eating: "进食", sleeping: "睡觉", playing: "玩耍", restless: "躁动", idle: "安静", moving: "走动",
};

export default function Home() {
  const [pet, setPet] = useState<PetProfile | null>(null);
  const [ov, setOv] = useState<Overview | null>(null);
  const [interps, setInterps] = useState<Interpretation[]>([]);
  const [health, setHealth] = useState<HealthAlert[]>([]);
  const [llm, setLlm] = useState<{ backend: string; available: boolean } | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [p, o, i, h, l] = await Promise.all([
        api.getPet(), api.getOverview(), api.getInterpretations(),
        api.getHealthAlerts(), api.llmStatus(),
      ]);
      setPet(p); setOv(o); setInterps(i); setHealth(h); setLlm(l); setErr(null);
    } catch {
      setErr(`无法连接服务端（${api.baseUrl}）。请确认本地服务已启动。`);
    }
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 6000);
    return () => clearInterval(t);
  }, [load]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  if (!pet) {
    return (
      <View style={s.center}>
        {err ? <Text style={s.err}>{err}</Text> : <ActivityIndicator color={C.acc} />}
      </View>
    );
  }

  const topAct = Object.entries(ov?.activities || {}).sort((a, b) => b[1] - a[1])[0];

  return (
    <ScrollView
      style={{ backgroundColor: C.bg }}
      contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={C.acc} />}
    >
      {/* 首页 3D 形象 + 概览 */}
      <View style={s.card}>
        <View style={s.hero}>
          <View style={s.pet3d}>
            <Text style={{ fontSize: 56 }}>{pet.species === "cat" ? "🐈" : "🐕"}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={s.petName}>{pet.name}</Text>
            <Text style={s.petSub}>{pet.breed || pet.species}</Text>
            <Text style={s.summary}>{ov?.summary || "正在观察…"}</Text>
          </View>
        </View>
        <View style={s.metrics}>
          <Metric b={topAct ? ACT[topAct[0]] || topAct[0] : "—"} s="主要状态" />
          <Metric b={`${ov?.vocal_count ?? 0} 次`} s="发声" />
          <Metric b={`${Object.values(ov?.actions || {}).reduce((x, y) => x + y, 0)} 次`} s="设备动作" />
        </View>
        <Text style={s.tag3d}>🧊 3D 形态图（示意，个体化重建见路线图）</Text>
      </View>

      {/* 听懂我 */}
      <Section title="👂 听懂我 · 情绪与需求解读">
        {interps.length === 0 && <Text style={s.mut}>还在观察中…</Text>}
        {interps.slice().reverse().slice(0, 6).map((i) => (
          <View key={i.id} style={s.item}>
            <View style={s.itemHead}>
              <Text style={s.itemLabel}>{i.label}</Text>
              <Text style={s.conf}>{Math.round(i.confidence * 100)}%</Text>
            </View>
            <Text style={s.ev}>依据：{i.evidence.join("；")}</Text>
          </View>
        ))}
        <Text style={s.disc}>做状态/需求解读，不是逐词翻译，每条带依据与置信度。</Text>
      </Section>

      {/* 看到我 + 互动 */}
      <SeeMe />

      {/* 了解宠物（对话下钻） */}
      <AskBox llmOn={!!llm?.available} />

      {/* 健康 */}
      <Section title="🩺 健康提示（提示，非诊断）">
        {health.length === 0 ? (
          <Text style={[s.mut, { color: C.ok }]}>暂无异常提示。</Text>
        ) : (
          health.map((h) => (
            <View key={h.id} style={[s.alert, h.severity === "urgent" && s.alertUrgent]}>
              <Text style={s.itemLabel}>{h.region}：{h.finding}</Text>
              <Text style={s.ev}>{h.evidence.join("；")} · 建议：{h.advice}</Text>
            </View>
          ))
        )}
        <Text style={s.disc}>本提示不构成诊断，请以兽医检查为准。</Text>
      </Section>

      {err && <Text style={s.err}>{err}</Text>}
    </ScrollView>
  );
}

function SeeMe() {
  const [text, setText] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  async function run(fn: () => Promise<unknown>, ok: string) {
    try { await fn(); setMsg(ok); } catch { setMsg("下发失败，检查服务端连接"); }
    setTimeout(() => setMsg(null), 2000);
  }
  return (
    <Section title="💬 看到我 · 远程互动">
      <TextInput
        style={s.input}
        value={text}
        onChangeText={setText}
        placeholder="用它熟悉的话安抚，如：Lucky 乖，马上回家"
        placeholderTextColor={C.mut}
      />
      <View style={s.btnRow}>
        <Btn label="用主人声音说" onPress={() => text.trim() && run(() => api.speak(text.trim()), "已播放")} primary />
        <Btn label="逗它玩" onPress={() => run(() => api.play("laser"), "开始逗玩")} />
        <Btn label="投零食" onPress={() => run(() => api.feed(), "已投食")} />
      </View>
      <Text style={s.disc}>宠物对熟悉的词 + 熟悉的声音响应最好，所以用主人声音而非陌生合成音。</Text>
      {msg && <Text style={[s.ev, { color: C.ok }]}>{msg}</Text>}
    </Section>
  );
}

function AskBox({ llmOn }: { llmOn: boolean }) {
  const [q, setQ] = useState("它今天怎么样？");
  const [ans, setAns] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  async function ask() {
    setLoading(true);
    try { const r = await api.ask(q); setAns(r.answer); } catch { setAns("查询失败"); }
    setLoading(false);
  }
  return (
    <Section title={`🔍 了解宠物${llmOn ? "" : "（规则版，接 LLM 更自然）"}`}>
      <TextInput style={s.input} value={q} onChangeText={setQ} placeholderTextColor={C.mut} />
      <View style={s.btnRow}>
        <Btn label={loading ? "思考中…" : "问问它"} onPress={ask} primary />
      </View>
      {ans && <Text style={[s.summary, { marginTop: 8 }]}>{ans}</Text>}
    </Section>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={s.card}>
      <Text style={s.secTitle}>{title}</Text>
      {children}
    </View>
  );
}
function Metric({ b, s: sub }: { b: string; s: string }) {
  return (
    <View style={s.metric}>
      <Text style={s.metricB}>{b}</Text>
      <Text style={s.metricS}>{sub}</Text>
    </View>
  );
}
function Btn({ label, onPress, primary }: { label: string; onPress: () => void; primary?: boolean }) {
  return (
    <Pressable style={[s.btn, primary ? s.btnPrimary : s.btnGhost]} onPress={onPress}>
      <Text style={[s.btnTxt, primary ? s.btnTxtPrimary : s.btnTxtGhost]}>{label}</Text>
    </Pressable>
  );
}

const s = StyleSheet.create({
  center: { flex: 1, backgroundColor: C.bg, alignItems: "center", justifyContent: "center", padding: 24 },
  card: { backgroundColor: C.card, borderRadius: 14, borderWidth: 1, borderColor: C.line, padding: 16, marginBottom: 14 },
  hero: { flexDirection: "row", gap: 14, alignItems: "center" },
  pet3d: {
    width: 92, height: 92, borderRadius: 16, backgroundColor: C.card2,
    alignItems: "center", justifyContent: "center",
  },
  petName: { color: C.txt, fontSize: 20, fontWeight: "700" },
  petSub: { color: C.mut, fontSize: 13, marginBottom: 6 },
  summary: { color: C.txt, fontSize: 14, lineHeight: 20 },
  metrics: { flexDirection: "row", gap: 10, marginTop: 14 },
  metric: { flex: 1, backgroundColor: C.card2, borderRadius: 10, padding: 10, alignItems: "center" },
  metricB: { color: C.txt, fontSize: 17, fontWeight: "700" },
  metricS: { color: C.mut, fontSize: 11, marginTop: 2 },
  tag3d: { color: C.mut, fontSize: 11, marginTop: 12, textAlign: "center" },
  secTitle: { color: C.mut, fontSize: 13, fontWeight: "600", marginBottom: 12, letterSpacing: 0.5 },
  item: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: C.line },
  itemHead: { flexDirection: "row", justifyContent: "space-between" },
  itemLabel: { color: C.txt, fontSize: 14, flex: 1 },
  conf: { color: C.mut, fontSize: 12 },
  ev: { color: C.mut, fontSize: 12, marginTop: 3 },
  mut: { color: C.mut, fontSize: 13 },
  disc: { color: C.mut, fontSize: 11, marginTop: 10, paddingTop: 8, borderTopWidth: 1, borderTopColor: C.line },
  input: {
    backgroundColor: C.card2, color: C.txt, borderRadius: 10, borderWidth: 1, borderColor: C.line,
    paddingHorizontal: 12, paddingVertical: 11, fontSize: 15,
  },
  btnRow: { flexDirection: "row", gap: 8, marginTop: 10, flexWrap: "wrap" },
  btn: { borderRadius: 10, paddingVertical: 11, paddingHorizontal: 14, flexGrow: 1, alignItems: "center" },
  btnPrimary: { backgroundColor: C.acc },
  btnGhost: { backgroundColor: C.card2, borderWidth: 1, borderColor: C.line },
  btnTxt: { fontSize: 14, fontWeight: "600" },
  btnTxtPrimary: { color: "#06243a" },
  btnTxtGhost: { color: C.txt },
  alert: { backgroundColor: C.card2, borderLeftWidth: 3, borderLeftColor: C.warn, borderRadius: 8, padding: 10, marginBottom: 8 },
  alertUrgent: { borderLeftColor: C.urgent },
  err: { color: C.urgent, fontSize: 13, textAlign: "center", marginTop: 10 },
});
