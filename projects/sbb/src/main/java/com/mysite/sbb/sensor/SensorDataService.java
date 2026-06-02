package com.mysite.sbb.sensor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Random;

import org.springframework.stereotype.Service;

@Service
public class SensorDataService {

    private final SensorDataRepository sensorDataRepository;

    public SensorDataService(SensorDataRepository sensorDataRepository) {
        this.sensorDataRepository = sensorDataRepository;
    }

    public List<SensorData> getList() {
        return this.sensorDataRepository.findAll();
    }

    public List<SensorData> getNormalData() {
        return this.sensorDataRepository.findByLabel("NORMAL");
    }

    public void create(String equipmentName, Double temperature, Double pressure,
            Double vibration, Double gasFlow, String label) {

        SensorData data = new SensorData();
        data.setEquipmentName(equipmentName);
        data.setTemperature(temperature);
        data.setPressure(pressure);
        data.setVibration(vibration);
        data.setGasFlow(gasFlow);
        data.setLabel(label);
        data.setCreateDate(LocalDateTime.now());

        this.sensorDataRepository.save(data);
    }

    public void generateSampleData() {
        Random random = new Random();

        for (int i = 1; i <= 20; i++) {
            create("Etcher-01",
                    65 + random.nextDouble() * 15,
                    1.7 + random.nextDouble() * 0.8,
                    0.1 + random.nextDouble() * 0.4,
                    100 + random.nextDouble() * 35,
                    "NORMAL");
        }

        for (int i = 1; i <= 10; i++) {
            create("Etcher-01",
                    90 + random.nextDouble() * 15,
                    3.5 + random.nextDouble() * 1.5,
                    1.3 + random.nextDouble() * 1.2,
                    170 + random.nextDouble() * 50,
                    "ABNORMAL");
        }
    }
}