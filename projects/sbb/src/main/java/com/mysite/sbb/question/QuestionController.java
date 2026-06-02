package com.mysite.sbb.question;

import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import lombok.RequiredArgsConstructor;

@RequestMapping("/question")
@RequiredArgsConstructor
@Controller
public class QuestionController {

    private final QuestionService questionService;

    // 질문 목록 조회
    @GetMapping("/list")
    public String list(Model model) {
        List<Question> questionList = this.questionService.getList();
        model.addAttribute("questionList", questionList);
        return "question_list";
    }

    // 질문 상세 조회
    @GetMapping(value = "/detail/{id}")
    public String detail(Model model, @PathVariable("id") Integer id) {
        Question question = this.questionService.getQuestion(id);
        model.addAttribute("question", question);
        return "question_detail";
    }

    // 질문 등록 화면 호출
    @GetMapping("/create")
    public String questionCreate() {
        return "question_form";
    }

    // 질문 등록 처리
    @PostMapping("/create")
    public String questionCreate(@RequestParam(value = "subject") String subject,
                                 @RequestParam(value = "content") String content) {
        this.questionService.create(subject, content);
        return "redirect:/question/list"; // 질문 저장 후 질문 목록으로 이동
    }

    // 질문 수정 화면 호출
    @GetMapping("/modify/{id}")
    public String questionModify(Model model, @PathVariable("id") Integer id) {
        Question question = this.questionService.getQuestion(id);
        model.addAttribute("question", question);
        return "question_modify";
    }

	    // 질문 수정 처리
	    @PostMapping("/modify/{id}")
	    public String questionModify(@PathVariable("id") Integer id, 
	                                 @RequestParam("subject") String subject, 
	                                 @RequestParam("content") String content) {
	        Question question = this.questionService.getQuestion(id);
	        this.questionService.modify(question, subject, content);
	        return String.format("redirect:/question/detail/%s", id);
	    }
	
	    // 질문 삭제 처리
	    @GetMapping("/delete/{id}")
	    public String questionDelete(@PathVariable("id") Integer id) {
	        Question question = this.questionService.getQuestion(id);
	        this.questionService.delete(question);
	        return "redirect:/question/list";
	    }
}