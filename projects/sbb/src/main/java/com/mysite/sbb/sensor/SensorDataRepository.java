package com.mysite.sbb.sensor;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface SensorDataRepository extends JpaRepository<SensorData, Integer> {

    List<SensorData> findByLabel(String label);
}