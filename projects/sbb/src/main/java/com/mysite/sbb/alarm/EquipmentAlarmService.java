package com.mysite.sbb.alarm;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.stereotype.Service;

@Service
public class EquipmentAlarmService {

    private final EquipmentAlarmRepository equipmentAlarmRepository;

    public EquipmentAlarmService(EquipmentAlarmRepository equipmentAlarmRepository) {
        this.equipmentAlarmRepository = equipmentAlarmRepository;
    }

    public List<EquipmentAlarm> getList() {
        return this.equipmentAlarmRepository.findAll();
    }

    public EquipmentAlarm getAlarm(Integer id) {
        return this.equipmentAlarmRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("알람 데이터를 찾을 수 없습니다."));
    }

    public EquipmentAlarm createManual(String equipmentName, String alarmCode, String alarmLevel, String message) {
        return saveAlarm(equipmentName, alarmCode, alarmLevel, message, null);
    }

    public EquipmentAlarm createAuto(String equipmentName, String message, Integer predictionResultId) {
        String alarmCode = "AI-" + System.currentTimeMillis();
        return saveAlarm(equipmentName, alarmCode, "CRITICAL", message, predictionResultId);
    }

    private EquipmentAlarm saveAlarm(String equipmentName,
                                     String alarmCode,
                                     String alarmLevel,
                                     String message,
                                     Integer predictionResultId) {

        EquipmentAlarm alarm = new EquipmentAlarm();

        alarm.setEquipmentName(equipmentName);
        alarm.setAlarmCode(alarmCode);
        alarm.setAlarmLevel(alarmLevel);
        alarm.setMessage(message);
        alarm.setPredictionResultId(predictionResultId);
        alarm.setCreateDate(LocalDateTime.now());

        return this.equipmentAlarmRepository.save(alarm);
    }

    public void saveAction(Integer id, String actionMemo) {
        EquipmentAlarm alarm = getAlarm(id);

        alarm.setActionMemo(actionMemo);
        alarm.setActionDate(LocalDateTime.now());

        this.equipmentAlarmRepository.save(alarm);
    }
}