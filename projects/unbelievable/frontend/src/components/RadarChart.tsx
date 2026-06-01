"use client";

import React from "react";
import {
  ResponsiveContainer,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip
} from "recharts";

interface RadarDataPoint {
  axisCode?: string;
  subject: string;
  자가진단_결과: number; // Survey score
  실제_분석값: number;  // Actual score
}

interface ScoreWarning {
  axis: string;
  axis_name?: string;
  code: string;
  message: string;
}

interface RadarChartProps {
  data: RadarDataPoint[];
  scoreWarnings?: ScoreWarning[];
}

export default function RadarChart({ data, scoreWarnings = [] }: RadarChartProps) {
  const warningByAxis = React.useMemo(() => {
    return scoreWarnings.reduce<Record<string, ScoreWarning>>((acc, warning) => {
      acc[warning.axis] = warning;
      return acc;
    }, {});
  }, [scoreWarnings]);

  const renderTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;

    const point = payload[0]?.payload as RadarDataPoint | undefined;
    const warning = point?.axisCode ? warningByAxis[point.axisCode] : undefined;
    const title = label || point?.subject;

    return (
      <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-xs shadow-xl">
        <div className="font-bold text-slate-950">{title}</div>
        {payload.map((entry: any) => (
          <div key={entry.dataKey} className="mt-1 flex items-center justify-between gap-4 text-slate-600">
            <span>{entry.name}</span>
            <span className="font-bold" style={{ color: entry.color }}>
              {Number(entry.value).toFixed(1)}점
            </span>
          </div>
        ))}
        {warning && (
          <div className="mt-2 rounded-lg border border-amber-200 bg-amber-50 px-2 py-1 text-[10px] font-semibold text-amber-700">
            해석 제한: 참고용 지표
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="relative h-[360px] w-full overflow-hidden rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="absolute top-4 left-6">
        <h3 className="font-heading text-lg font-black text-slate-950">자가진단과 실제 기록 비교</h3>
        <p className="text-xs font-semibold text-slate-500">내 생각과 실제 기록의 차이를 6개 지표로 봅니다.</p>
      </div>
      
      <div className="w-full h-full pt-8">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsRadar cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#cbd5e1" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: "#475569", fontSize: 12, fontWeight: 700 }}
            />
            <PolarRadiusAxis 
              angle={30} 
              domain={[0, 100]} 
              tick={{ fill: "#94a3b8" }}
              axisLine={false}
            />
            
            {/* Subjective Survey (Blue Glow) */}
            <Radar
              name="자가진단 결과 (예측)"
              dataKey="자가진단_결과"
              stroke="#0f766e"
              fill="#0f766e"
              fillOpacity={0.18}
            />
            
            {/* Objective Actual (Purple Glow) */}
            <Radar
              name="실제 분석 결과 (사후)"
              dataKey="실제_분석값"
              stroke="#e11d48"
              fill="#e11d48"
              fillOpacity={0.22}
            />
            
            <Tooltip content={renderTooltip} />
            <Legend 
              wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }}
              align="center"
              verticalAlign="bottom"
            />
          </RechartsRadar>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
