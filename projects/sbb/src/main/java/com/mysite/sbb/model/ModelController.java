package com.mysite.sbb.model;

import java.util.Optional;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/model")
public class ModelController {

    private final ModelService modelService;

    public ModelController(ModelService modelService) {
        this.modelService = modelService;
    }

    @GetMapping("/train")
    public String train() {
        this.modelService.trainModel();
        return "redirect:/model/info";
    }

    @GetMapping("/info")
    public String info(Model model) {
        Optional<ModelInfo> modelInfo = this.modelService.getLatestModelOptional();

        model.addAttribute("modelInfo", modelInfo.orElse(null));

        return "model_info";
    }
}