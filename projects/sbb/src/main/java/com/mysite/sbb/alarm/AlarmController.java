package com.mysite.sbb.alarm;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
@RequestMapping("/alarm")
public class AlarmController {

    private final EquipmentAlarmService equipmentAlarmService;

    public AlarmController(EquipmentAlarmService equipmentAlarmService) {
        this.equipmentAlarmService = equipmentAlarmService;
    }

    @GetMapping("/list")
    public String list(Model model) {
        model.addAttribute("alarmList", this.equipmentAlarmService.getList());
        return "alarm_list";
    }

    @GetMapping("/detail/{id}")
    public String detail(Model model, @PathVariable("id") Integer id) {
        model.addAttribute("alarm", this.equipmentAlarmService.getAlarm(id));
        return "alarm_detail";
    }

    @GetMapping("/create")
    public String createForm() {
        return "alarm_form";
    }

    @PostMapping("/create")
    public String create(@RequestParam("equipmentName") String equipmentName,
                         @RequestParam("alarmCode") String alarmCode,
                         @RequestParam("alarmLevel") String alarmLevel,
                         @RequestParam("message") String message) {

        this.equipmentAlarmService.createManual(equipmentName, alarmCode, alarmLevel, message);

        return "redirect:/alarm/list";
    }

    @PostMapping("/action/{id}")
    public String action(@PathVariable("id") Integer id,
                         @RequestParam("actionMemo") String actionMemo) {

        this.equipmentAlarmService.saveAction(id, actionMemo);

        return "redirect:/alarm/detail/" + id;
    }
}