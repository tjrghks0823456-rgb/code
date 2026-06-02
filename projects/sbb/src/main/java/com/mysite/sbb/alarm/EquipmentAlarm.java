package com.mysite.sbb.alarm;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class EquipmentAlarm {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String equipmentName;
    private String alarmCode;
    private String alarmLevel;

    @Column(columnDefinition = "TEXT")
    private String message;

    private Integer predictionResultId;
    private String actionMemo;
    private LocalDateTime createDate;
    private LocalDateTime actionDate;

    public Integer getId() {
        return id;
    }

    public String getEquipmentName() {
        return equipmentName;
    }

    public void setEquipmentName(String equipmentName) {
        this.equipmentName = equipmentName;
    }

    public String getAlarmCode() {
        return alarmCode;
    }

    public void setAlarmCode(String alarmCode) {
        this.alarmCode = alarmCode;
    }

    public String getAlarmLevel() {
        return alarmLevel;
    }

    public void setAlarmLevel(String alarmLevel) {
        this.alarmLevel = alarmLevel;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Integer getPredictionResultId() {
        return predictionResultId;
    }

    public void setPredictionResultId(Integer predictionResultId) {
        this.predictionResultId = predictionResultId;
    }

    public String getActionMemo() {
        return actionMemo;
    }

    public void setActionMemo(String actionMemo) {
        this.actionMemo = actionMemo;
    }

    public LocalDateTime getCreateDate() {
        return createDate;
    }

    public void setCreateDate(LocalDateTime createDate) {
        this.createDate = createDate;
    }

    public LocalDateTime getActionDate() {
        return actionDate;
    }

    public void setActionDate(LocalDateTime actionDate) {
        this.actionDate = actionDate;
    }
}