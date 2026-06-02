package com.mysite.sbb.sensor;

import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
@RequestMapping("/sensor")
public class SensorDataController {

    private final SensorDataService sensorDataService;

    public SensorDataController(SensorDataService sensorDataService) {
        this.sensorDataService = sensorDataService;
    }

    @GetMapping("/list")
    public String list(Model model) {
        List<SensorData> sensorDataList = this.sensorDataService.getList();
        model.addAttribute("sensorDataList", sensorDataList);
        return "sensor_list";
    }

    @GetMapping("/create")
    public String createForm() {
        return "sensor_form";
    }

    @PostMapping("/create")
    public String create(
            @RequestParam("equipmentName") String equipmentName,
            @RequestParam("temperature") Double temperature,
            @RequestParam("pressure") Double pressure,
            @RequestParam("vibration") Double vibration,
            @RequestParam("gasFlow") Double gasFlow,
            @RequestParam("label") String label) {

        this.sensorDataService.create(equipmentName, temperature, pressure, vibration, gasFlow, label);
        return "redirect:/sensor/list";
    }

    @GetMapping("/generate")
    public String generate() {
        this.sensorDataService.generateSampleData();
        return "redirect:/sensor/list";
    }
}