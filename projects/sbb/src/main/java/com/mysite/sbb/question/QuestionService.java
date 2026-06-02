package com.mysite.sbb.question;

import java.util.List;
import java.util.Optional;
import java.time.LocalDateTime;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;

import com.mysite.sbb.DataNotFoundException;

@RequiredArgsConstructor
@Service
public class QuestionService {

    private final QuestionRepository questionRepository;

    public List<Question> getList() {
        return this.questionRepository.findAll();
    }

    public Question getQuestion(Integer id) {
        Optional<Question> question = this.questionRepository.findById(id);
        if (question.isPresent()) {
            return question.get();
        } else {
            throw new DataNotFoundException("question not found");
        }
    }

    public void create(String subject, String content) {
        Question q = new Question();
        q.setSubject(subject);
        q.setContent(content);
        q.setCreateDate(LocalDateTime.now());
        this.questionRepository.save(q);
    }
    
    // 수정 포인트 1: String subject와 String content 사이에 콤마(,) 추가
    public void modify(Question question, String subject, String content) {
        question.setSubject(subject);
        question.setContent(content);
        // 수정 시에도 수정 일시를 저장하고 싶다면 아래 코드를 추가할 수 있습니다.
        // question.setModifyDate(LocalDateTime.now()); 
        this.questionRepository.save(question);
    }
    
    public void delete(Question question) {
        this.questionRepository.delete(question);
    }
} // 수정 포인트 2: 불필요하게 닫혀있던 중괄호 정리