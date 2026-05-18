using System.Collections.Generic;

namespace SemiToolHMI.Models
{
    /// <summary>
    /// 레시피 헤더 + 스텝 목록
    /// DB의 recipe_header + recipe_step 구조를 그대로 담는 모델
    /// </summary>
    public class Recipe
    {
        public int RecipeId { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }

        public List<RecipeStep> Steps { get; set; }

        public Recipe()
        {
            Steps = new List<RecipeStep>();
        }
    }
}
