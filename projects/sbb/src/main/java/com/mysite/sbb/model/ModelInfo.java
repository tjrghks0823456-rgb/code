package com.mysite.sbb.model;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class ModelInfo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private Double avgTemperature;
    private Double avgPressure;
    private Double avgVibration;
    private Double avgGasFlow;
    private Integer trainDataCount;
    private LocalDateTime trainDate;

    public Integer getId() {
        return id;
    }

    public Double getAvgTemperature() {
        return avgTemperature;
    }

    public void setAvgTemperature(Double avgTemperature) {
        this.avgTemperature = avgTemperature;
    }

    public Double getAvgPressure() {
        return avgPressure;
    }

    public void setAvgPressure(Double avgPressure) {
        this.avgPressure = avgPressure;
    }

    public Double getAvgVibration() {
        return avgVibration;
    }

    public void setAvgVibration(Double avgVibration) {
        this.avgVibration = avgVibration;
    }

    public Double getAvgGasFlow() {
        return avgGasFlow;
    }

    public void setAvgGasFlow(Double avgGasFlow) {
        this.avgGasFlow = avgGasFlow;
    }

    public Integer getTrainDataCount() {
        return trainDataCount;
    }

    public void setTrainDataCount(Integer trainDataCount) {
        this.trainDataCount = trainDataCount;
    }

    public LocalDateTime getTrainDate() {
        return trainDate;
    }

    public void setTrainDate(LocalDateTime trainDate) {
        this.trainDate = trainDate;
    }
}