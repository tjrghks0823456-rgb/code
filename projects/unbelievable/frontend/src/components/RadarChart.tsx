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
  subject: string;
  자가진단_결과: number; // Survey score
  실제_분석값: number;  // Actual score
}

interface RadarChartProps {
  data: RadarDataPoint[];
}

export default function RadarChart({ data }: RadarChartProps) {
  return (
    <div className="w-full h-[360px] bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      <div className="absolute top-4 left-6">
        <h3 className="text-lg font-bold text-white font-heading">메타인지 편향성 비교 차트</h3>
        <p className="text-xs text-slate-400">사전 자가진단(예측)과 사후 실제 데이터 분석 결과 대조</p>
      </div>
      
      <div className="w-full h-full pt-8">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsRadar cx="50%" cy="50%" outerRadius="75%" data={data}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: "#94a3b8", fontSize: 12, fontWeight: 500 }}
            />
            <PolarRadiusAxis 
              angle={30} 
              domain={[0, 100]} 
              tick={{ fill: "#64748b" }}
              axisLine={false}
            />
            
            {/* Subjective Survey (Blue Glow) */}
            <Radar
              name="자가진단 결과 (예측)"
              dataKey="자가진단_결과"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.15}
            />
            
            {/* Objective Actual (Purple Glow) */}
            <Radar
              name="실제 분석 결과 (사후)"
              dataKey="실제_분석값"
              stroke="#a855f7"
              fill="#a855f7"
              fillOpacity={0.3}
            />
            
            <Tooltip 
              contentStyle={{ background: "#0f172a", borderColor: "#1e293b", color: "#f8fafc" }}
            />
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
