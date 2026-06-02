package com.mysite.sbb;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;


@Controller
public class lombokcontroller {

	@GetMapping("/lombok")
	@ResponseBody
	public String lombokTest() {
		
		lomboktest data =new lomboktest();
		
		data.setEquipmentName("Etcher");
		data.setTemperature(85.5);
		
		return "장비명 : " + data.getEquipmentName()+ 	
		       "/온도 : "	 + data.getTemperature();
	}
}
